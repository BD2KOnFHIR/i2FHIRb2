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

from i2fhirb2.removefacts import list_test_artifacts
from tests.utils.connection_helper import connection_helper
from tests.utils.crc_testcase import CRCTestCase


class CRCTestCaseTestCase(CRCTestCase):

    def test_clean_exit(self):
        """ Determine whether the test cases all cleaned up after themselves """
        ch = connection_helper()
        qr = list_test_artifacts(None, ch.tables)
        self.assertFalse(bool(qr), """Run 'removefacts --conf <config> --removetestlist' or 
execute 'tests/scripts/removetestfacts.py' to fix""")

    def test_sourcesystem_cd(self):
        """ Test CRCTestCase.sourcesystem_cd() nesting """
        with self.sourcesystem_cd():
            self.assertEqual("test_i2FHIRb2_" + type(self).__name__, self._sourcesystem_cd)
            with self.sourcesystem_cd():
                self.assertEqual("test_i2FHIRb2_" + type(self).__name__, self._sourcesystem_cd)
        self.assertIsNone(getattr(self, "_sourcesystem_cd", None))
        self.assertIsNone(getattr(self, "_upload_id", None))

    @unittest.expectedFailure
    def test_sourcesystem_cd_2(self):
        """ Test CRCTestCase.sourcesystem_cd() assertion failure processing """
        with self.sourcesystem_cd():
            self.assertEqual("test_i2FHIRb2_" + type(self).__name__, self._sourcesystem_cd)
            self.assertEqual(117651, self._upload_id)
            self.assertTrue(False)

    def test_zsourcesystem_cd(self):
        """ Second half of ``test_sourcesystem_cd_2`` test """
        self.assertIsNone(getattr(self, "_sourcesystem_cd", None))


if __name__ == '__main__':
    unittest.main()
