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
import os
import unittest
from collections import OrderedDict

import datetime

from isodate import FixedOffset
from rdflib import Graph

from tests.utils.base_test_case import test_data_directory


class FHIRPatientDimensionTestCase(unittest.TestCase):
    def test_load_ttl(self):
        from i2fhirb2.fhir.fhirpatientdimension import FHIRPatientDimension
        from i2fhirb2.fhir.fhirspecific import FHIR
        from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientMapping
        from i2fhirb2.i2b2model.data.i2b2patientdimension import PatientDimension

        PatientMapping._clear()
        PatientMapping.update_date = datetime.datetime(2017, 5, 25)
        PatientMapping.sourcesystem_cd = "FHIR"
        PatientMapping.upload_id = 12345

        PatientDimension._clear()
        PatientDimension.update_date = datetime.datetime(2017, 5, 25)
        PatientDimension.sourcesystem_cd = "FHIR"
        PatientDimension.upload_id = 12345

        g = Graph()
        g.load(os.path.join(os.path.split(os.path.abspath(__file__))[0], "data", "patient-example.ttl"), format="turtle")
        s = FHIR['Patient/example']
        pd_entry = FHIRPatientDimension(g, s)

        self.assertEqual(OrderedDict([
             ('patient_num', 100000001),
             ('vital_status_cd', 'UH'),
             ('birth_date',
              datetime.datetime(1974, 12, 25, 14, 35, 45, tzinfo=FixedOffset(-5))),
             ('death_date', None),
             ('sex_cd', 'M'),
             ('age_in_years_num', 43),
             ('language_cd', None),
             ('race_cd', None),
             ('marital_status_cd', None),
             ('religion_cd', None),
             ('zip_cd', '3999'),
             ('statecityzip_path', 'Zip codes\\Vic\\PleasantVille\\3999\\'),
             ('income_cd', None),
             ('patient_blob', None),
             ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', 12345)]), pd_entry.patient_dimension_entry._freeze())

        self.assertEqual(2, len(pd_entry.patient_mappings.patient_mapping_entries))
        self.assertEqual(OrderedDict([
             ('patient_ide', 'example'),
             ('patient_ide_source', 'http://hl7.org/fhir/'),
             ('patient_num', 100000001),
             ('patient_ide_status', 'A'),
             ('project_id', 'fhir'),
             ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', 12345)]), pd_entry.patient_mappings.patient_mapping_entries[0]._freeze())
        self.assertEqual(OrderedDict([
            ('patient_ide', '100000001'),
             ('patient_ide_source', 'HIVE'),
             ('patient_num', 100000001),
             ('patient_ide_status', 'A'),
             ('project_id', 'fhir'),
             ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', 12345)]), pd_entry.patient_mappings.patient_mapping_entries[1]._freeze())


if __name__ == '__main__':
    unittest.main()
