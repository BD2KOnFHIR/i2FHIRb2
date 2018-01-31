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

from tests.utils.base_test_case import test_data_directory, test_conf_directory
from tests.utils.crc_testcase import CRCTestCase

conf_file = os.path.join(test_conf_directory, 'db_conf')
med_desp_upload_id = 2020
pat_upload_id = 2021


class PatientDimensionScriptTestCase(CRCTestCase):

    @unittest.skip
    def test1(self):
        from i2fhirb2.loadfacts import load_facts

        data_file = os.path.join(test_data_directory, 'medicationdispense0308.ttl')
        with self.sourcesystem_cd():
            load_facts(f"-i {data_file} -l --conf {conf_file} -u {med_desp_upload_id} -ss {self._sourcesystem_cd}".
                       split())
            self.assertEqual(True, False)

    @unittest.skip
    def test2(self):
        from i2fhirb2.loadfacts import load_facts

        data_file = "http://hl7.org/fhir/Patient/pat1"
        with self.sourcesystem_cd():
            load_facts(f"-i {data_file} -l --conf {conf_file} -u {pat_upload_id} -ss {self._sourcesystem_cd}".split())
            self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
