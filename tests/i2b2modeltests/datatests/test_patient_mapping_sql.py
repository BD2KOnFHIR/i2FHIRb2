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

from tests.utils.connection_helper import connection_helper


class PatientMappingSQLTestCase(unittest.TestCase):
    opts = connection_helper()

    def test_insert(self):
        from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientMapping, PatientIDEStatus

        print("{} records deleted".format(PatientMapping.delete_upload_id(self.opts.tables, self.opts.uploadid)))
        PatientMapping.upload_id = self.opts.uploadid
        pm = PatientMapping(10000001, "12345", PatientIDEStatus.active, "http://hl7.org/fhir/", "fhir")

        n_upd, n_ins = PatientMapping.add_or_update_records(self.opts.tables, [pm])
        self.assertEqual((0, 1), (n_upd, n_ins))
        n_upd, n_ins = PatientMapping.add_or_update_records(self.opts.tables, [pm])
        self.assertEqual((0, 0), (n_upd, n_ins))
        pm._project_id = "TEST"

        pm2 = PatientMapping(10000001, "12346", PatientIDEStatus.active, "http://hl7.org/fhir/", "fhir")
        n_upd, n_ins = PatientMapping.add_or_update_records(self.opts.tables, [pm, pm2])
        self.assertEqual((0, 2), (n_upd, n_ins))
        self.assertEqual(3, PatientMapping.delete_upload_id(self.opts.tables, self.opts.uploadid))


if __name__ == '__main__':
    unittest.main()
