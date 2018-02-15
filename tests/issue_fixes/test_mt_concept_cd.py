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

from tests.utils.base_test_case import test_data_directory
from tests.utils.load_facts_helper import LoadFactsHelper


class MtConceptTestCase(LoadFactsHelper):
    caller_filename = __file__

    def test_mt_concept_code(self):
        """ Test for a problem encountered in SMARTONFHIR load where concept_cd was null """
        test_dir = os.path.join(test_data_directory, 'smartonfhir_testdata', 'samples')
        with self.sourcesystem_cd():
            self.load_named_resource('mt_concept_cd.json', test_dir)
        self.assertTrue(True)

    def test_loinc_concept_code(self):
        """ Test for a problem encountered in SMARTONFHIR load where concept_cd was null """
        test_dir = os.path.join(test_data_directory, 'smartonfhir_testdata', 'samples')
        with self.sourcesystem_cd():
            self.load_named_resource('obs_sample_1134281.ttl', test_dir)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
