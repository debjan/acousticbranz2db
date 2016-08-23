## http://acousticbrainz.org migrations

#### 1. to Postgres

```shell
$ python3 ab2pg.py -h
usage: ab2pg.py [-h] [--database DATABASE] [--user USER] [--password PASSWORD]
                [--host HOST] [--port PORT] [--tables TABLES] [--debug]
                filename

Populate PostgreSQL database from a file with MUSICBRAINZ_TRACKIDs with
AcousticBrainz low_level and/or high_level datasets. More information
about AcousticBrainz at: http://acousticbrainz.org/

positional arguments:
  filename             file with MUSICBRAINZ_TRACKID lines

optional arguments:
  -h, --help           show this help message and exit
  --database DATABASE  the database name
  --user USER          user name used to authenticate
  --password PASSWORD  password used to authenticate
  --host HOST          database host address
  --port PORT          connection port number
  --tables TABLES
  --debug              print debug messages
```

#### 2. to MongoDB

```shell
$ python3 ab2mongo.py -h
usage: ab2mongo.py [-h] [--database DATABASE] [--host HOST] [--port PORT]
                   [--collections COLLECTIONS] [--debug]
                   filename

Populate MongoDB database from a file with MUSICBRAINZ_TRACKIDs with
AcousticBrainz low_level and/or high_level datasets. More information about
AcousticBrainz at: http://acousticbrainz.org/

positional arguments:
  filename              file with MUSICBRAINZ_TRACKID lines

optional arguments:
  -h, --help            show this help message and exit
  --database DATABASE   the database name
  --host HOST           hostname or IP address of a single mongod
  --port PORT           port number on which to connect
  --collections COLLECTIONS
  --debug               print debug messages
```
