# Copyright (c) 2017, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the Mayo Clinic nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import shlex
from argparse import ArgumentParser, Namespace
from typing import List, Tuple

from sqlalchemy import MetaData, create_engine, Table, Column
from sqlalchemy.engine import Engine

Default_DB_Connection = "postgresql+psycopg2://localhost:5432/i2b2"
Default_User = "postgres"
Default_Password = "postgres"

def add_connection_args(parser: ArgumentParser) -> ArgumentParser:
    """
    Add the database connection arguments to the supplied parser
    :param parser: parser to add arguments to
    :return: parser
    """
    parser.add_argument("-db", "--dburl", help="Default database URL (default: {})".format(Default_DB_Connection),
                        default=Default_DB_Connection)
    parser.add_argument("--user", help="Default user name (default: {})".format(Default_User),
                        default=Default_User)
    parser.add_argument("--password", help="Default password (default: {})".format(Default_Password),
                        default=Default_Password)
    parser.add_argument("--crcdb", help="CRC database URL.  (default: dburl)")
    parser.add_argument("--crcuser", help="User name for CRC database. (default: user)")
    parser.add_argument("--crcpassword", help="Password for CRC database. (default: password")
    parser.add_argument("--ontdb", help="Ontology database URL.  (default: dburl)")
    parser.add_argument("--ontuser", help="User name for ontology database. (default: user)")
    parser.add_argument("--ontpassword", help="Password for ontology database. (default: password)")
    return parser


def process_parsed_args(opts: Namespace) -> Namespace:
    """
    Set the defaults for the crc and ontology schemas
    :param opts: parsed arguments
    :return: namespace with additional elements added
    """
    def setdefault(vn: str, default: object) -> None:
        assert vn in opts, "Unknown option"
        if not getattr(opts, vn):
            setattr(opts, vn, default)

    setdefault('crcdb', opts.dburl)
    setdefault('crcuser', opts.user)
    setdefault('crcpassword', opts.password)
    setdefault('ontdb', opts.dburl)
    setdefault('ontuser', opts.user)
    setdefault('ontpassword', opts.password)
    opts.tables = I2B2Tables(opts)
    return opts


def decode_file_args(argv: List[str]) -> List[str]:
    """
    Preprocess any arguments that begin with an '@' sign.  This replaces the one in Argparse because it
    a) doesn't process "-x y" correctly and b) ignores bad files
    :param argv: raw options list
    :return: options list with file references replaced
    """
    for arg in [arg for arg in argv if arg[0] == '@']:
        argv.remove(arg)
        with open(arg[1:]) as config_file:
            argv += shlex.split(config_file.read())
            return decode_file_args(argv)
    return argv


class I2B2Tables:
    """
    Class that represents the set of i2b2 tables that are used in this package.  The actual tables
    can be accessed by:
        t = I2B2Tables(opts)
        t.visit_dimension       # Specific table
        t.crc_engine            # Engine for crc tables
        t.crc_connection        # Connection for crc tables
    """
    i2b2metadata = 'i2b2metadata'
    i2b2crc = 'i2b2demodata'

    def __init__(self, opts: Namespace):
        _metadata = MetaData()
        crc_url, ont_url = self._db_urls(opts)

        self.crc_engine = create_engine(crc_url)
        self.crc_connection = self.crc_engine.connect()
        _metadata.reflect(bind=self.crc_engine, schema=self.i2b2crc)
        self._crc_tables = _metadata.tables
        if ont_url != crc_url:
            self.ont_engine = create_engine(ont_url)
            self.ont_connection = self.ont_engine.connect()
        else:
            self.ont_engine = self.crc_engine
            self.ont_connection = self.crc_connection

        _metadata.reflect(bind=self.ont_engine, schema=self.i2b2metadata)
        self._ont_tables = _metadata.tables

    # Note: If you get a recursion error below, you've got an unitialized self variable in the __init__ section
    def __getattr__(self, item):
        k = I2B2Tables.i2b2metadata + '.' + item
        if k in self._ont_tables:
            return self._ont_tables[k]
        k = I2B2Tables.i2b2crc + '.' + item
        if k in self._crc_tables:
            return self._crc_tables[k]
        return None

    def __getitem__(self, item):
        return getattr(self, item)

    @staticmethod
    def _db_urls(opts: Namespace) -> Tuple[str, str]:
        """
        Return the crc and ontology db urls
        :param opts: options
        :return: Tuple w/ crc and ontology url
        """
        return opts.crcdb.replace("//", "//{crcuser}:{crcpassword}@".format(**opts.__dict__)),\
            opts.ontdb.replace("//", "//{ontuser}:{ontpassword}@".format(**opts.__dict__))

    def _tables(self) -> List[Tuple[str, str]]:
        """
        Return a list of all known tables and and its full URI
        :return: table name and full URI
        """
        return [(k.rsplit('.', 1)[1] if '.' in k else k, k) for k in self._ont_tables.keys()]


def change_column_length(table: Table, column: Column, length: int, engine: Engine) -> None:
    """ Change the column length in the supplied table
    """
    if column.type.length < length:
        print("Changing length of {} from {} to {}".format(column, column.type.length, length))
        column.type.length = length
        column_name = column.name
        column_type = column.type.compile(engine.dialect)
        engine.execute('ALTER TABLE {table} ALTER COLUMN {column_name} TYPE {column_type}'.format(**locals()))
