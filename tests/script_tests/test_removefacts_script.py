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

from i2fhirb2.removefacts import remove_facts
from tests.utils.script_test_base import ScriptTestBase


class RemoveFactsTestCase(ScriptTestBase):
    dirname, _ = os.path.split(os.path.abspath(__file__))

    @classmethod
    def setUpClass(cls):
        cls.dirname = os.path.split(os.path.abspath(__file__))[0]
        cls.save_output = False
        cls.tst_dir = "removefacts"
        cls.tst_fcn = remove_facts

    def test_no_args(self):
        self.check_output_output("", "noargs")

    def test_help(self):
        self.check_output_output("-h", "help", exception=True)

    def test_onearg(self):
        self.check_output_output("123450", "onearg")

    def test_threeargs(self):
        self.check_output_output("123450 123460 123470", "threeargs")

    def test_sourcesystem(self):
        self.check_output_output("--sourcesystemcd SAMPLE", "sourcesystem")

    def test_ss_and_id(self):
        self.check_output_output("123450 --sourcesystemcd SAMPLE", "ssandid")

    def test_config_parms(self):
        self.check_output_output("--conf {} 123450".format(os.path.join(self.dirname, 'data', 'db_conf')), "confparms")


if __name__ == '__main__':
    unittest.main()
