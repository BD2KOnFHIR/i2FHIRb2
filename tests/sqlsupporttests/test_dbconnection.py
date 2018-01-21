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
import os

from i2fhirb2.sqlsupport.dbconnection import process_parsed_args
from i2fhirb2.file_aware_parser import FileAwareParser


class DBConnectionTestCase(unittest.TestCase):
    dirname, _ = os.path.split(os.path.abspath(__file__))

    def test_decodefileargs1(self):
        from i2fhirb2.sqlsupport.dbconnection import add_connection_args

        parser = FileAwareParser()
        parser.add_argument('-mv', '--metadatavoc', help="Unused")
        add_connection_args(parser)
        opts = parser.parse_args(parser.decode_file_args("--conf {}".
                                                         format(os.path.join(self.dirname, 'data', 'db_conf')).split()))
        self.assertEqual("postgresql+psycopg2://localhost:5432/i2b2", opts.crcdb)
        self.assertEqual("postgresql+psycopg2://localhost:5433/i2b2", opts.ontodb)
        self.assertEqual("postgresql+psycopg2://localhost:5431/i2b2", opts.dburl)
        self.assertEqual('../tests/data/fhir_metadata_vocabulary', opts.metadatavoc)
        self.assertEqual('postgres', opts.user)
        self.assertEqual('postgres', opts.password)

    def test_decodefileargs2(self):
        from i2fhirb2.sqlsupport.dbconnection import add_connection_args

        parser = FileAwareParser()
        add_connection_args(parser)
        opts = process_parsed_args(
            parser.parse_args(
                parser.decode_file_args("--conf {}".format(os.path.join(self.dirname, 'data', 'db_conf_2')).split())),
            None, False)
        self.assertEqual("postgresql+psycopg2://localhost:5431/i2b2", opts.crcdb)
        self.assertEqual("user2", opts.crcuser)
        self.assertEqual("password1", opts.crcpassword)
        self.assertEqual("postgresql+psycopg2://localhost:5433/i2b2", opts.ontodb)
        self.assertEqual("postgresql+psycopg2://localhost:5431/i2b2", opts.dburl)
        self.assertEqual('user1', opts.ontouser)
        self.assertEqual('password1', opts.ontopassword)


if __name__ == '__main__':
    unittest.main()
