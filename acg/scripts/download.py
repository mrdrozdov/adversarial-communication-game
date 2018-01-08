"""

Extract a sample of data that can used for crowdflower.

"""

import logging
import random

import os
import json
import errno
import requests
import argparse

import time
import transaction
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )
from server.models.meta import Base
from server.models import Example, Label, ExampleFile
from server.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from sqlalchemy.sql.expression import func, select


here = os.path.realpath(__file__)


LOG = None


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


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
    """

    1. Read all urls.
    2. Save images to some nested directories.
    3. Save path to images in the database.

    Example Path:

        image:
        /flickr/{short_resource_id}/{uuid}/1.jpg
        description:
        /flickr/{short_resource_id}/{uuid}/1.json

    """
    logger = initialize_logger()

    logger.info("Begin.")

    config_uri = args.config_uri
    settings = get_appsettings(config_uri, options={}, name='myapp')

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    img_dir = args.image_directory


    def example_iterator():
        if args.random:
            for ex in dbsession.query(Example).order_by(func.rand()).limit(10).all():
                yield ex
        else:
            with transaction.manager:
                dbsession = get_tm_session(session_factory, transaction.manager)
                labels = dbsession.query(Label).all()
                for label in labels:
                    for ex in label.examples:
                        yield ex


    for example in example_iterator():
        short_resource_id = example.resource_id[:4]
        guid = example.id.hex
        prefix = os.path.join(img_dir, "flickr", short_resource_id, guid)
        img_path = os.path.join(prefix, "1.jpg")
        desc_path = os.path.join(prefix, "1.json")
        mkdir_p(prefix)

        if os.path.isfile(img_path):
            continue

        # Download Image
        example_url = json.loads(example.flickr_data).get("url_m", None)
        if example_url is None:
            example_url = json.loads(example.flickr_data).get("url_z", None)
        if example_url is None:
            example_url = json.loads(example.flickr_data).get("url_s", None)
        if example_url is None:
            raise Exception("No example url.")
        response = requests.get(example_url)
        with open(img_path, 'wb') as f:
            f.write(response.content)

        # Save Description
        flickr_data = json.loads(example.flickr_data)
        meta = dict(flickr_data=flickr_data, url=example_url)
        with open(desc_path, 'w') as f:
            f.write(json.dumps(meta))

        # Add row to database.
        with transaction.manager:
            dbsession = get_tm_session(session_factory, transaction.manager)
            example_file = ExampleFile(img_path=img_path, desc_path=desc_path, example=example)
            dbsession.add(example_file)

        # Logging
        logger.info(img_path)
        logger.info(desc_path)

        time.sleep(args.sleep)


def main():
    timestamp = int(time.time())
    default_preview_file = os.path.abspath(os.path.join(here, "..", "resource", "preview.csv"))
    default_output_file = os.path.abspath(os.path.join(here, "..", "resource", "crowdflower_{}.csv".format(timestamp)))
    default_image_directory = os.path.abspath(os.path.join(os.path.expanduser("~"), "data", "acg", "images"))

    parser = argparse.ArgumentParser()
    parser.add_argument("config_uri", type=str, help="Path to config file.")
    parser.add_argument("--preview_file", type=str, help="Path to preview data used in crowdflower.",
                        default=default_preview_file)
    parser.add_argument("--per_label", default=10, type=int, help="Number of images to use per label.")
    parser.add_argument("--output_file", type=str, help="Number of images to use per label.",
                        default=default_output_file)
    parser.add_argument("--skip_db", action="store_true", help="If set, will generate file without updating database.")
    parser.add_argument("--skip_shuffle", action="store_true", help="If set, will not shuffle results.")
    parser.add_argument("--image_directory", default=default_image_directory, type=str, help="Directory for saved images.")
    parser.add_argument("--sleep", default=0.01, type=float, help="Time to wait between calls.")
    parser.add_argument("--random", action="store_true", help="Randomly select some images to download. Good for debugging.")
    options = parser.parse_args()

    print(json.dumps(options.__dict__, indent=4, sort_keys=True))

    run(options)


if __name__ == "__main__":
    main()
