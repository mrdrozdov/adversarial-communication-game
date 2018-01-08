"""

Extract a sample of data that can used for crowdflower.

"""

import logging
import random

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
from sqlalchemy.sql.expression import func, select


here = os.path.realpath(__file__)


LOG = None


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

    1. Read preview_file to get viable labels.
    2. For each label, get all existing GUIDs of examples that have been used for crowdflower.
    3. Select N examples that haven't been used for crowdflower.

    :param args:
    :return:
    """
    logger = initialize_logger()

    logger.info("Begin.")

    config_uri = args.config_uri
    settings = get_appsettings(config_uri, options={}, name='myapp')

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        labels = {}

        # Read Eligible Classes and Preview URLs
        with open(os.path.abspath(args.preview_file)) as f:
            col_index = {}
            col_vals = []
            for i, line in enumerate(f):
                # Read Header
                if i == 0:
                    keys = line.strip().split(",")
                    for j, k in enumerate(keys):
                        col_index[k] = j
                    col_vals = [k for k in keys]
                    continue

                # Read Row

                cols = line.strip().split(",")

                label_dict = dict(name=cols[col_index["name"]],
                                  val=cols[col_index["value"]],
                                  image_1_url=cols[col_index["image_1_url"]],
                                  image_2_url=cols[col_index["image_2_url"]],
                                  image_3_url=cols[col_index["image_3_url"]])

                labels[label_dict["val"]] = label_dict

        label_names = list(labels.keys())

        header = ",".join([
            "image_url",
            "label_{i}_name,label_{i}_value,label_{i}_image_1,label_{i}_image_2,label_{i}_image_3".format(i=1),
            "label_{i}_name,label_{i}_value,label_{i}_image_1,label_{i}_image_2,label_{i}_image_3".format(i=2),
            "label_{i}_name,label_{i}_value,label_{i}_image_1,label_{i}_image_2,label_{i}_image_3".format(i=3),
            ])

        row_tpl = "{" + "},{".join(header.split(",")) + "}"

        rows = []

        print(header)
        print(row_tpl)

        N_LABELS = 3

        # Randomly Sample Examples from Data
        for k, v in labels.items():
            label_name = k
            examples = dbsession.query(Example)\
                     .join(Example.label, aliased=True)\
                     .filter_by(name=label_name)\
                     .order_by(func.rand())\
                     .limit(args.per_label)\
                     .all()
            for example in examples:

                # choose random other classes

                candidate_labels = set()
                candidate_labels.add(label_name)

                while len(candidate_labels) < N_LABELS:
                    candidate_label = label_names[random.randint(0, len(label_names)-1)]
                    if candidate_label in candidate_labels:
                        continue
                    candidate_labels.add(candidate_label)

                row_dict = {}

                example_url = json.loads(example.flickr_data).get("url_m", None)
                if example_url is None:
                    example_url = json.loads(example.flickr_data).get("url_z", None)
                if example_url is None:
                    example_url = json.loads(example.flickr_data).get("url_s", None)
                if example_url is None:
                    raise Exception("No example url.")

                row_dict.update(image_url=example_url)

                for ic, candidate_label in enumerate(sorted(candidate_labels)):
                    row_dict.update({
                        "label_{i}_name".format(i=ic+1): labels[candidate_label]["name"],
                        "label_{i}_value".format(i=ic+1): labels[candidate_label]["val"],
                        "label_{i}_image_1".format(i=ic+1): labels[candidate_label]["image_1_url"],
                        "label_{i}_image_2".format(i=ic+1): labels[candidate_label]["image_2_url"],
                        "label_{i}_image_3".format(i=ic+1): labels[candidate_label]["image_3_url"]
                    })

                row = row_tpl.format(**row_dict)
                rows.append(row)

        random.shuffle(rows)

        # Write rows to output file.
        with open(args.output_file, "w") as f:
            f.write(header + "\n")
            for row in rows:
                f.write(row + "\n")


def main():
    timestamp = int(time.time())
    default_preview_file = os.path.abspath(os.path.join(here, "..", "resource", "preview.csv"))
    default_output_file = os.path.abspath(os.path.join(here, "..", "resource", "crowdflower_{}.csv".format(timestamp)))

    parser = argparse.ArgumentParser()
    parser.add_argument("config_uri", type=str, help="Path to config file.")
    parser.add_argument("--preview_file", type=str, help="Path to preview data used in crowdflower.",
                        default=default_preview_file)
    parser.add_argument("--per_label", default=10, type=int, help="Number of images to use per label.")
    parser.add_argument("--output_file", type=str, help="Number of images to use per label.",
                        default=default_output_file)
    parser.add_argument("--skip_db", action="store_true", help="If set, will generate file without updating database.")
    parser.add_argument("--skip_shuffle", action="store_true", help="If set, will not shuffle results.")
    options = parser.parse_args()

    print(json.dumps(options.__dict__, indent=4, sort_keys=True))

    run(options)


if __name__ == "__main__":
    main()
