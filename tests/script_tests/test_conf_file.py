# Copyright (c) 2018, Mayo Clinic
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

from i2fhirb2.conf_file import conf_file
from tests.utils.script_test_base import ScriptTestBase


class ConfFile(ScriptTestBase):

    @classmethod
    def setUpClass(cls):
        cls.dirname = os.path.split(os.path.abspath(__file__))[0]
        cls.save_output = False
        cls.tst_dir = "conf_file"
        cls.tst_fcn = conf_file

    def test_no_args(self):
        self.check_output_output("-f data/db_conf", "noargs")

    def test_version(self):
        self.check_output_output("-v", "version", exception=True)

    def test_help(self):
        self.check_output_output("-h", "help", exception=True)

    def test_multi_parms(self):
        self.check_error_output("-c --update", "multi")

    def test_create_error(self):
        with open(os.path.join(self.dirname, 'data', 'db_conf_mt'), 'w'):
            pass
        self.check_error_output("-f data/db_conf_mt -c", "create_error")

    def test_create_mt_file(self):
        self.check_output_output("-f data/db_conf_mt -c!", "create_mt")

    def test_create_std_file(self):
        self.check_output_output("-f data_out/conf_file/my_conf -c! -mv ../tests/data/fhir_metadata_vocabulary "
                                 "-db postgresql+psycopg2://localhost:5432/i2b2 --user postgres --password postgres",
                                 "std_conf")
        self.check_output_output("-f data_out/conf_file/my_conf", "show_std_conf")

    def test_create_bad_arg(self):
        self.check_error_output("-f data/db_conf_mt --badarg", "argerror")

    def test_all_args(self):
        argstr = "-mv metavoc -ss sourcesystemcode -u 17334 --base BASE -ub uribase -p provider -db dburl " \
                 "--user defuser --password defpassword --crcdb crcdburl --crcuser crcuser --crcpassword crcpwd " \
                 "--ontodb ontdburl --ontouser ontuser --ontopassword ontpasswd --onttable tables"
        self.check_output_output("-f data_out/conf_file/big_conf -c! " + argstr, "all_args")
        self.save_output = True
        self.check_output_output("-f data_out/conf_file/big_conf", "show_all_args")


if __name__ == '__main__':
    unittest.main()
