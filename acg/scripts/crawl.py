import logging

import flickrapi
import json
import os
import argparse

import transaction
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )
# from pyramid.scripts.common import parse_vars
from server.models.meta import Base
from server.models import Example, FlickrQuery, Label
from server.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )


class Crawler(object):
    def __init__(self, key, secret):
        self.flickr = flickrapi.FlickrAPI(key, secret, format='parsed-json')

    def search(self, query, page=0, per_page=100):
        return self.flickr.photos.search(
            extras='owner_name,description,tags,url_s,url_m,url_z',
            media='photos',
            content_type=1,
            text=query,
            sort='relevance',
            per_page=per_page,
            page=page
        )


def run(args):
    crawler = Crawler(args.key, args.secret)

    response = crawler.search(args.query,
                              page=args.page,
                              per_page=args.per_page)
    print(len(response["photos"]["photo"]))
    # print(json.dumps(response, indent=4, sort_keys=True))

    config_uri = args.config_uri
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options={}, name='myapp')

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        flickr_query = FlickrQuery(query=args.query)
        dbsession.add(flickr_query)

        label = dbsession.query(Label).filter_by(name=args.label).first()
        if label is None:
            label = Label(name=args.label)
            dbsession.add(label)

        for photo in response["photos"]["photo"]:
            example = Example(label=label,
                              flickr_query=flickr_query,
                              flickr_data=json.dumps(photo))
            dbsession.add(example)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_uri", type=str, help="Path to config file.")
    parser.add_argument("--key", default=None, type=str, help="Flickr API key.")
    parser.add_argument("--secret", default=None, type=str, help="Flickr API secret.")
    parser.add_argument("--label", default="baboon", type=str, help="Image label.")
    parser.add_argument("--query", default="baboon animal", type=str, help="Flickr query.")
    parser.add_argument("--page", default=0, type=int, help="Query parameter. Offset.")
    parser.add_argument("--per_page", default=2, type=int, help="Query parameter. Results per page.")
    options = parser.parse_args()

    if options.key is None:
        options.key = os.environ.get("FLICKR_KEY", None)

    if options.secret is None:
        options.secret = os.environ.get("FLICKR_SECRET", None)

    run(options)


if __name__ == "__main__":
    main()
