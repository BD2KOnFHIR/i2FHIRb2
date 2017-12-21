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
import re
import unittest

import os
import io
import sys
from functools import reduce

from i2fhirb2.removefacts import remove_facts
from tests.utils.script_test_base import ScriptTestBase

from i2fhirb2.loadfacts import load_facts
from tests.utils.base_test_case import test_conf_file, test_upload_id, test_sourcesystem_cd


class Issue8TestCase(ScriptTestBase):
    enc_re = r'Starting encounter number: (\d+)'
    pat_re = r'Starting patient number: (\d+)'
    triples_re = r'\d+ triples'
    org_pat = r'\d+.*\(Organization\).*'
    pat_pat = r'\d+.*\(Patient\).*'
    obs_pat = r'\d+.*\(Observation\).*'
    del_patterns = [enc_re, pat_re, triples_re, org_pat, pat_pat, obs_pat]

    @staticmethod
    def reset_facts():
        save_stdout = sys.stdout
        sys.stdout = io.StringIO()
        remove_facts(f"{test_upload_id} --conf {test_conf_file}".split())
        sys.stdout = save_stdout

    @classmethod
    def setUpClass(cls):
        cls.dirname = os.path.split(os.path.abspath(__file__))[0]
        cls.save_output = False
        cls.tst_dir = "issue8"
        cls.tst_fcn = load_facts
        cls.reset_facts()

    @classmethod
    def tearDownClass(cls):
        cls.reset_facts()

    def test_patient_dimension_issue(self):
        argstr = f"--conf {test_conf_file} -l -t json -u {test_upload_id} " \
                 f"--sourcesystem {test_sourcesystem_cd} -i http://hl7.org/fhir/patient-example.json"
        self.check_filtered_output(argstr, "first_load", self._filter_results)
        first_enc_num = self._start_enc_number      # No encounter (visit) numbers are generated in this test
        first_pat_num = self._start_pat_num + 1

        self.check_filtered_output(argstr, "second_load", self._filter_results)
        self.assertEqual(first_enc_num, self._start_enc_number)
        self.assertEqual(first_pat_num, self._start_pat_num)

        self.check_filtered_output(argstr, "third_load", self._filter_results)
        self.assertEqual(first_enc_num, self._start_enc_number)
        self.assertEqual(first_pat_num, self._start_pat_num)

        # Now add an encounter and make sure things still work out
        argstr = f"--conf {test_conf_file} -l -t json -u {test_upload_id} " \
                 f"--sourcesystem {test_sourcesystem_cd} -i http://hl7.org/fhir/observation-example-bmi.json"
        self.check_filtered_output(argstr, "obs_load", self._filter_results)
        self.assertEqual(first_enc_num, self._start_enc_number)
        self.assertEqual(first_pat_num, self._start_pat_num)

    def _filter_results(self, inp: str) -> str:
        self._start_enc_number = int(re.search(r'Starting encounter number: (\d+)', inp).groups()[0])
        self._start_pat_num = int(re.search(r'Starting patient number: (\d+)', inp).groups()[0])
        return reduce(lambda txt, p: re.sub(p, '', txt), self.del_patterns, inp)


if __name__ == '__main__':
    unittest.main()
