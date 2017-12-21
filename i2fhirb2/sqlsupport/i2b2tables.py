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
from argparse import Namespace
from typing import Tuple, List

from sqlalchemy import MetaData, create_engine, Table, Column
from sqlalchemy.engine import Engine

from i2fhirb2.i2b2model.shared.tablenames import i2b2tablenames


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

    def __init__(self, opts: Namespace) -> None:
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
        phys_name = i2b2tablenames.phys_name(item)
        k = I2B2Tables.i2b2metadata + '.' + phys_name
        if k in self._ont_tables:
            return self._ont_tables[k]
        k = I2B2Tables.i2b2crc + '.' + phys_name
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
            opts.ontodb.replace("//", "//{ontouser}:{ontopassword}@".format(**opts.__dict__))

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
