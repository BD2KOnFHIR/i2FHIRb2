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

from i2fhirb2.fhir.fhirpatientmapping import PatientNumberGenerator
from tests.utils.connection_helper import connection_helper


class FHIRPatientMappingTestCase(unittest.TestCase):
    def test_patient_mapping(self):
        from i2fhirb2.fhir.fhirpatientmapping import FHIRPatientMapping
        from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientMapping

        PatientMapping._clear()
        PatientMapping.update_date = datetime(2017, 5, 25)
        PatientMapping.sourcesystem_cd = "FHIR"
        FHIRPatientMapping._clear()
        PatientMapping.upload_id = 1773486

        pm = FHIRPatientMapping(connection_helper().tables, "p123", "http://hl7.org/fhir")

        self.assertEqual(OrderedDict([
             ('patient_ide', 'p123'),
             ('patient_ide_source', 'http://hl7.org/fhir'),
             ('patient_num', 100000001),
             ('patient_ide_status', 'A'),
             ('project_id', 'fhir'),
             ('update_date', datetime(2017, 5, 25, 0, 0)),
             ('download_date', datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', 1773486)]), pm.patient_mapping_entries[0]._freeze())
        self.assertEqual(OrderedDict([
             ('patient_ide', '100000001'),
             ('patient_ide_source', 'HIVE'),
             ('patient_num', 100000001),
             ('patient_ide_status', 'A'),
             ('project_id', 'fhir'),
             ('update_date', datetime(2017, 5, 25, 0, 0)),
             ('download_date', datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', 1773486)]), pm.patient_mapping_entries[1]._freeze())
        self.assertEqual(2, len(pm.patient_mapping_entries))

        pm2 = FHIRPatientMapping(connection_helper().tables, "p123", "http://hl7.org/fhir")
        self.assertEqual(2, len(pm.patient_mapping_entries))
        self.assertEqual(pm2.patient_num, pm.patient_num)

    def test_patientnum_refresh(self):
        # Not a lot we can do to test this without knowing what is in the database.   We COULD add something to the
        # tables and demonstrate that we don't see it if we pass a number in...
        png = PatientNumberGenerator(10000)
        self.assertEqual(png.new_number(), 10000)
        self.assertEqual(png.new_number(), 10001)
        opts = connection_helper()
        png.refresh(opts.tables, None)
        print("Next patient number: {}".format(png.new_number()))
        self.assertNotEqual(png.new_number(), 10002)
        png.refresh(opts.tables, 4321)
        self.assertNotEqual(png.new_number(), 10002)


if __name__ == '__main__':
    unittest.main()
