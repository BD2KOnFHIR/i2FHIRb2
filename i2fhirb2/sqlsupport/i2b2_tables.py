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
from typing import Optional

from sqlalchemy import MetaData, create_engine, Table, select


class I2B2Tables:
    i2b2metadata = 'i2b2metadata'
    i2b2crc = 'i2b2demodata'

    def __init__(self):
        self._metadata = MetaData()
        self.engine = create_engine('postgresql+psycopg2://i2b2:demouser@localhost:5432/i2b2')
        self.connection = self.engine.connect()
        self._metadata.reflect(bind=self.engine, schema=self.i2b2metadata)
        self._metadata_tables = self._metadata.tables
        self._metadata.reflect(bind=self.engine, schema=self.i2b2crc)
        self._crc_tables = self._metadata_tables

    def __getattr__(self, item):
        k = I2B2Tables.i2b2metadata + '.' + item
        if k in self._metadata_tables:
            return self._metadata_tables[k]
        k = I2B2Tables.i2b2crc + '.' + item
        if k in self._crc_tables:
            return self._crc_tables[k]
        return None

    def __getitem__(self, item):
        return getattr(self, item)