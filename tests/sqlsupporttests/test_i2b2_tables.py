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
import os
import unittest
from sqlalchemy import select

from i2fhirb2.sqlsupport.dbconnection import process_parsed_args


def caught_error(message):
    raise ValueError(message)  # reraise an error


# NOTE: if you get a "no tests" error, it is because parse_args does an exit(1).  Chances are
# the issue is in the location of the db_conf file
class I2B2TablesTestCase(unittest.TestCase):
    from i2fhirb2.generate_i2b2 import genargs
    conf_file = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..', 'conf', 'db_conf'))

    opts = genargs('-l --conf {} '.format(conf_file).split())
    process_parsed_args(opts)

    def test_basics(self):
        from i2fhirb2.sqlsupport.dbconnection import I2B2Tables
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
        s = select([x.i2b2]).order_by(x.i2b2.c.c_hlevel).limit(10)

        for e in x.crc_engine.execute(s).fetchall():
            self.assertTrue(e[0] < 2)

    def test_as_dict(self):
        from i2fhirb2.sqlsupport.dbconnection import I2B2Tables
        x = I2B2Tables(self.opts)

        self.assertEqual(x.concept_dimension, x['concept_dimension'])


if __name__ == '__main__':
    unittest.main()
