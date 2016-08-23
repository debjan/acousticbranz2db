#! python3

"""Populate PostgreSQL database from a file with MUSICBRAINZ_TRACKIDs with
AcousticBrainz low_level and/or high_level datasets.

More information about AcousticBrainz at: http://acousticbrainz.org/
"""

import logging
import os
import sys
from urllib.request import HTTPError, urlopen

import psycopg2
from psycopg2.extras import Json, register_default_jsonb


def make_connection(args):
    """Connect to database (create and populate if it does not exist)
    """
    def check_db(cursor, database):
        cursor.execute("SELECT 1 FROM pg_database WHERE datname=(%s)", (database,))
        return bool(cursor.rowcount)

    def check_table(cursor, table):
        cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name=(%s)", (table,))
        return bool(cursor.rowcount)

    def create_table(cursor, table):
        cursor.execute("CREATE TABLE %s (mbid UUID PRIMARY KEY, data jsonb NOT NULL)" % table)
        logging.debug('Table "%s" created' % table)

    try:
        conn = psycopg2.connect(**args)
    except psycopg2.OperationalError:
        database = args.pop('database')
        args['database'] = 'postgres'
        conn = psycopg2.connect(**args)
        conn.autocommit = True
        with conn.cursor() as cursor:
            if not check_db(cursor, database):
                cursor.execute("CREATE DATABASE %s" % database)
            assert check_db(cursor, database), 'Database creation failed!'
            logging.debug('Database "%s" created' % database)
            for table in tables:
                if not check_table(cursor, table):
                    create_table(cursor, table)

    return conn


def get_data(mbid, table):
    url = 'https://acousticbrainz.org/api/v1/%s/%s'
    try:
        with urlopen(url % (mbid, table.replace('_', '-'))) as request:
            return request.read().decode()
    except HTTPError:
        logging.warning('Not available MBID: %s' % mbid)


def main(args):

    filename = args.pop('filename')
    assert os.path.exists(filename), '"%s" does not exist!' % filename

    conn = make_connection(args)
    conn.autocommit = True
    register_default_jsonb(conn)

    with open(filename) as source:
        for mbid in [line.rstrip() for line in source.readlines()]:
            if len(mbid) == 36:
                for table in tables:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "SELECT 1 FROM {} WHERE mbid=(%s)".format(table),
                            (mbid,))
                        if not bool(cursor.rowcount):
                            data = get_data(mbid, table)
                            if data:
                                cursor.execute(
                                    "INSERT INTO {} VALUES (%s, %s)".format(table),
                                    (mbid, Json(data)))
                                logging.debug('"%s" insert: %s' % (table, mbid))
                            else:
                                break
                        else:
                            logging.debug('"%s" already exists!' % mbid)
            else:
                logging.warning('Incorrect MBID: %s' % mbid)

    conn.close()


if __name__ == '__main__':

    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('filename', help='file with MUSICBRAINZ_TRACKID lines')
    parser.add_argument('--database',
                        default='acoustic_brainz',
                        help='the database name')
    parser.add_argument('--user', help='user name used to authenticate')
    parser.add_argument('--password', help='password used to authenticate')
    parser.add_argument('--host', help='database host address')
    parser.add_argument('--port', help='connection port number')
    parser.add_argument('--tables', type=list, default=['high_level', 'low_level'])
    parser.add_argument('--debug',
                        required=False,
                        action='store_true',
                        help='print debug messages')

    args = parser.parse_args().__dict__
    tables = args.pop('tables')

    logging.basicConfig(stream=sys.stdout,
                        level=args.pop('debug') and logging.DEBUG or logging.WARNING)

    main(args)
