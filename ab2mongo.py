#! python3

"""Populate MongoDB database from a file with MUSICBRAINZ_TRACKIDs
with AcousticBrainz low_level and/or high_level datasets.

More information about AcousticBrainz at: http://acousticbrainz.org/
"""

import json
import logging
import os
import sys
from urllib.request import HTTPError, urlopen

import pymongo


def get_data(mbid, collection):
    url = 'https://acousticbrainz.org/api/v1/%s/%s'
    try:
        with urlopen(url % (mbid, collection.replace('_', '-'))) as request:
            return json.loads(request.read().decode())
    except HTTPError:
        logging.warning('Not available MBID: %s' % mbid)


def main(args):

    filename = args.pop('filename')
    assert os.path.exists(filename), '"%s" does not exist!'

    database = args.pop('database')
    client = pymongo.MongoClient(**args)
    db = client[database]

    with open(filename) as source:
        for mbid in [line.rstrip() for line in source.readlines()]:
            if len(mbid) == 36:
                for collection in collections:
                    col = db[collection]
                    if col.find({'_id': mbid}).count() == 0:
                        data = get_data(mbid, collection)
                        if data:
                            document = {'_id': mbid}
                            document['data'] = data
                            col.insert_one(document)
                            logging.debug('"%s" insert: %s' % (collection, mbid))
                        else:
                            break
                    else:
                        logging.debug('"%s" already exists!' % mbid)
            else:
                logging.warning('Invalid MBID: %s' % mbid)


if __name__ == '__main__':

    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('filename', help='file with MUSICBRAINZ_TRACKID lines')
    parser.add_argument('--database',
                        default='acoustic_brainz',
                        help='the database name')
    parser.add_argument('--host', help='hostname or IP address of a single mongod')
    parser.add_argument('--port', help='port number on which to connect')
    parser.add_argument('--collections', type=list, default=['high_level', 'low_level'])
    parser.add_argument('--debug',
                        required=False,
                        action='store_true',
                        help='print debug messages')

    args = parser.parse_args().__dict__
    collections = args.pop('collections')

    logging.basicConfig(stream=sys.stdout,
                        level=args.pop('debug') and logging.DEBUG or logging.WARNING)

    main(args)
