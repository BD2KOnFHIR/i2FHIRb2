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
from collections import OrderedDict
from datetime import datetime

from tests.utils.crc_testcase import CRCTestCase


class PatientMappingTestCase(CRCTestCase):
    def test_patient_mapping(self):
        from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientMapping
        from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientIDEStatus

        PatientMapping._clear()
        PatientMapping.update_date = datetime(2017, 5, 25)
        with self.sourcesystem_cd():
            PatientMapping.sourcesystem_cd = self._sourcesystem_cd
            pm = PatientMapping(10000001, "p123", PatientIDEStatus.active, "http://hl7.org/fhir/", "fhir")
            PatientMapping.upload_id = 17443

            self.assertEqual(OrderedDict([
                 ('patient_ide', 'p123'),
                 ('patient_ide_source', 'http://hl7.org/fhir/'),
                 ('patient_num', 10000001),
                 ('patient_ide_status', 'A'),
                 ('project_id', 'fhir'),
                 ('update_date', datetime(2017, 5, 25, 0, 0)),
                 ('download_date', datetime(2017, 5, 25, 0, 0)),
                 ('import_date', datetime(2017, 5, 25, 0, 0)),
                 ('sourcesystem_cd', self._sourcesystem_cd),
                 ('upload_id', 17443)]), pm._freeze())


if __name__ == '__main__':
    unittest.main()
