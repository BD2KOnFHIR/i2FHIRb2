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

import unittest
from argparse import ArgumentParser

from sqlalchemy import select


def caught_error(message):
    raise ValueError(message)  # reraise an error


class I2B2TablesTestCase(unittest.TestCase):
    from i2fhirb2.generate_i2b2 import genargs

    opts = genargs(['x', '@data/db_conf'])

    def test_basics(self):
        from i2fhirb2.sqlsupport.i2b2_tables import I2B2Tables
        x = I2B2Tables(self.opts)

        self.assertEqual(['concept_path',
                          'concept_cd',
                          'name_char',
                          'concept_blob',
                          'update_date',
                          'download_date',
                          'import_date',
                          'sourcesystem_cd',
                          'upload_id'], x.concept_dimension.columns.keys())
        s = select([x.i2b2]).limit(10)

        # We kind of blindly assume that the first 10 records in the file are level 1...
        for e in x.crc_engine.execute(s).fetchall():
            self.assertEqual(e[0], 1)

    def test_as_dict(self):
        from i2fhirb2.sqlsupport.i2b2_tables import I2B2Tables
        x = I2B2Tables(self.opts)

        self.assertEqual(x.concept_dimension, x['concept_dimension'])


if __name__ == '__main__':
    unittest.main()
