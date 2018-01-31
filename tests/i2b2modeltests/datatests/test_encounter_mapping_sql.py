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
from datetime import datetime

from tests.utils.connection_helper import connection_helper
from tests.utils.crc_testcase import CRCTestCase


class EncounterMappingSQLTest(CRCTestCase):
    opts = connection_helper()

    def test_insert(self):
        from i2fhirb2.i2b2model.data.i2b2encountermapping import EncounterMapping, EncounterIDEStatus

        EncounterMapping.delete_upload_id(self.opts.tables, self.opts.uploadid)
        EncounterMapping._clear()
        EncounterMapping.update_date = datetime(2017, 5, 25)
        EncounterMapping.upload_id = self.opts.uploadid

        with self.sourcesystem_cd() as ss_cd:
            EncounterMapping.sourcesystem_cd = self._sourcesystem_cd
            em = EncounterMapping("f001", "http://hl7.org/fhir", "FHIR", 5000017, "patient01",
                                  "http://hl7.org/fhir", EncounterIDEStatus.active)

            n_ins, n_upd = EncounterMapping.add_or_update_records(self.opts.tables, [em])
            self.assertEqual((0, 1), (n_upd, n_ins))
            n_ins, n_upd = EncounterMapping.add_or_update_records(self.opts.tables, [em])
            self.assertEqual((0, 0), (n_upd, n_ins))

            em._project_id = "TEST"
            em2 = EncounterMapping("f002", "http://hl7.org/fhir", "FHIR", 5000018, "patient02",
                                   "http://hl7.org/fhir", EncounterIDEStatus.active)
            n_ins, n_upd = EncounterMapping.add_or_update_records(self.opts.tables, [em, em2])
            self.assertEqual((0, 2), (n_upd, n_ins))
            self.assertEqual(3, EncounterMapping.delete_upload_id(self.opts.tables, self.opts.uploadid))


if __name__ == '__main__':
    unittest.main()
