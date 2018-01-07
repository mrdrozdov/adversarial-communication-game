import logging

import flickrapi
import json
import os
import argparse

import time
import transaction
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )
from server.models.meta import Base
from server.models import Example, FlickrQuery, FlickrQuerySet, Label
from server.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )


LOG = None


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


def initialize_logger():
    global LOG
    if LOG is None:
        # create logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

        LOG = logger
    else:
        logger = LOG

    return logger


def run(args):
    logger = initialize_logger()

    logger.info("Begin.")

    crawler = Crawler(args.key, args.secret)

    config_uri = args.config_uri
    settings = get_appsettings(config_uri, options={}, name='myapp')

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        flickr_query_set = FlickrQuerySet()
        dbsession.add(flickr_query_set)

    label_cache = {}

    for i in range(args.pages):
        label_name = args.label
        query = args.query
        page = args.page + i + 1
        per_page = args.per_page

        logger.info("Search (Request) label={label} query={query} page={page} per_page={per_page}".format(
            label=label_name, query=query, page=page, per_page=per_page
        ))

        response = crawler.search(query,
                                  page=page,
                                  per_page=per_page)

        total = len(response["photos"]["photo"])

        logger.info(
            "Search (Response) label={label} query={query} page={page} per_page={per_page} total={total}".format(
                label=label_name, query=query, page=page, per_page=per_page, total=total
            ))

        with transaction.manager:
            dbsession = get_tm_session(session_factory, transaction.manager)
            flickr_query = FlickrQuery(flickr_query_set=flickr_query_set,
                                       query=query,
                                       page=page,
                                       per_page=per_page,
                                       total=total)
            dbsession.add(flickr_query)

        with transaction.manager:
            dbsession = get_tm_session(session_factory, transaction.manager)
            label = label_cache.get(label_name, None)
            if label is None:
                label = dbsession.query(Label).filter_by(name=label_name).first()
                label_cache[label_name] = label
            if label is None:
                label = Label(name=label_name)
                dbsession.add(label)

            added = 0

            for j, photo in enumerate(response["photos"]["photo"]):
                resource_id = photo["id"]
                example = dbsession.query(Example).filter_by(resource_id=resource_id).first()
                if example is None:
                    try:
                        flickr_data = json.dumps(photo)
                        if len(flickr_data) > 4096:
                            raise ValueError("Too much flickr data.")
                        rank = (page-1) * per_page + j
                        assert rank > 0, \
                            "Rank specifies the order in the query's results, and should always be non-negative"
                        example = Example(label=label,
                                          resource_id=resource_id,
                                          rank=rank,
                                          flickr_query=flickr_query,
                                          flickr_data=flickr_data)
                        dbsession.add(example)
                        added += 1
                    except:
                        continue

        logger.info("Search label={label} query={query} page={page} per_page={per_page} added={added}".format(
            label=label_name, query=query, page=page, per_page=per_page, added=added
        ))

        time.sleep(args.sleep)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_uri", type=str, help="Path to config file.")
    parser.add_argument("--key", default=None, type=str, help="Flickr API key.")
    parser.add_argument("--secret", default=None, type=str, help="Flickr API secret.")
    parser.add_argument("--query_file", default=None, type=str, help="Set of queries.")
    parser.add_argument("--label", default="baboon", type=str, help="Image label.")
    parser.add_argument("--query", default="baboon animal", type=str, help="Flickr query.")
    parser.add_argument("--sleep", default=3, type=float, help="Throttle time between queries.")
    parser.add_argument("--pages", default=20, type=int, help="Query parameter. Number of pages.")
    parser.add_argument("--page", default=0, type=int, help="Query parameter. Offset.")
    parser.add_argument("--per_page", default=200, type=int, help="Query parameter. Results per page.")
    options = parser.parse_args()

    if options.key is None:
        options.key = os.environ.get("FLICKR_KEY", None)

    if options.secret is None:
        options.secret = os.environ.get("FLICKR_SECRET", None)

    print(json.dumps(options.__dict__, indent=4, sort_keys=True))

    if options.query_file is not None:
        with open(options.query_file) as f:
            for line in f:
                label, query = line.strip().split(",")

                if label.startswith("#"):
                    continue

                _options = argparse.Namespace(**vars(options))
                _options.label = label
                _options.query = query
                run(_options)
    else:
        run(options)


if __name__ == "__main__":
    main()
