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

# When loadfacts is run in working directory /Users/mrf7578/Development/git/BD2KOnFHIR/i2FHIRb2/i2fhirb2
# we get "FileNotFoundError: [Errno 2] No such file or directory:
# '/Users/mrf7578/Development/git/BD2KOnFHIR/i2FHIRb2/tests/tests/data/synthea_data/fhir/Zieme803_Caroline16_2.json'
#
# The issue -- the dbconnection decodeFileArgs function needs to make any relative file path *inside* a configuration
# relative to the configuration file, not the calling program.  It attempts to do this by adding rel_path to
# the parser.  This has two issues:
#   1) We have no way to know whether something IS a file reference within the config file and, when we DO know,
#      we don't know whether it was added from the (a) config file
#   2) Config files can be nested and/or occur multiple times.  There is only one rel_path
#
from i2fhirb2.loadfacts import create_parser
from i2fhirb2.sqlsupport.dbconnection import add_connection_args, decode_file_args

script_tmpl = "-i {}/data/synthea_data/fhir/Zieme803_Caroline16_2.json" \
              " -u 119651 -l -rm --conf {}/conf/db_conf --sourcesystem SMARTONFHIR"


class FilePathTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = os.path.abspath(os.path.dirname(__file__))
        testpath = os.path.abspath(os.path.join(base, '..', '..', 'tests'))
        cls._reltestpath = os.path.relpath(os.path.abspath(os.path.curdir), testpath)

    def test1(self):
        script = script_tmpl.format(self._reltestpath, self._reltestpath)
        parser = add_connection_args(create_parser())
        opts = parser.parse_args(decode_file_args(script.split(), parser))
        self.assertTrue(os.path.exists(opts.infile[0]))
        self.assertTrue(os.path.exists(opts.metadatavoc))


if __name__ == '__main__':
    unittest.main()
