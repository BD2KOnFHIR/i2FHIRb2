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

import datetime
from collections import OrderedDict

from isodate import FixedOffset
from rdflib import Graph, Literal, XSD

from i2fhirb2.fhir.fhirencountermapping import FHIREncounterMapping


class FHIRVisitDimensionTestCase(unittest.TestCase):

    def test_load_ttl(self):
        from i2fhirb2.fhir.fhirvisitdimension import FHIRVisitDimension
        from i2fhirb2.fhir.fhirspecific import FHIR
        from i2fhirb2.i2b2model.data.i2b2visitdimension import VisitDimension
        from i2fhirb2.i2b2model.data.i2b2encountermapping import EncounterMapping

        EncounterMapping._clear()
        EncounterMapping.update_date = datetime.datetime(2017, 5, 25)
        EncounterMapping.sourcesystem_cd = "FHIR"
        EncounterMapping.upload_id = 1700043

        VisitDimension._clear()
        VisitDimension.update_date = datetime.datetime(2017, 5, 25)
        VisitDimension.sourcesystem_cd = "FHIR"
        VisitDimension.upload_id = 1700043

        FHIREncounterMapping._clear()           # reset the encounter number generator

        g = Graph()
        g.load(os.path.join(os.path.split(os.path.abspath(__file__))[0], "data",
                            "diagnosticreport-example-f202-bloodculture.ttl"), format="turtle")
        pd_entry = FHIRVisitDimension(g.value(predicate=FHIR.nodeRole, object=FHIR.treeRoot), 100001,
                                      "f201", "http://hl7.org/fhir",
                                      Literal("2013-03-11T10:28:00+01:00", datatype=XSD.dateTime).toPython())

        self.assertEqual(OrderedDict([
             ('encounter_num', 500000),
             ('patient_num', 100001),
             ('active_status_cd', 'OA'),
             ('start_date',
              datetime.datetime(2013, 3, 11, 10, 28, tzinfo=FixedOffset(1))),
             ('end_date', None),
             ('inout_cd', None),
             ('location_cd', None),
             ('location_path', None),
             ('length_of_stay', None),
             ('visit_blob', None),
             ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', 1700043)]), pd_entry.visit_dimension_entry._freeze())

        self.assertEqual(OrderedDict([
             ('encounter_ide', 'f202'),
             ('encounter_ide_source', 'http://hl7.org/fhir/'),
             ('project_id', 'fhir'),
             ('encounter_num', 500000),
             ('patient_ide', 'f201'),
             ('patient_ide_source', 'http://hl7.org/fhir'),
             ('encounter_ide_status', 'A'),
             ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', 1700043)]), pd_entry.encounter_mappings.encounter_mapping_entries[0]._freeze())
        self.assertEqual(OrderedDict([
            ('encounter_ide', '500000'),
             ('encounter_ide_source', 'HIVE'),
             ('project_id', 'fhir'),
             ('encounter_num', 500000),
             ('patient_ide', 'f201'),
             ('patient_ide_source', 'http://hl7.org/fhir'),
             ('encounter_ide_status', 'A'),
             ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', 1700043)]), pd_entry.encounter_mappings.encounter_mapping_entries[1]._freeze())
        self.assertEqual(2, len(pd_entry.encounter_mappings.encounter_mapping_entries))



if __name__ == '__main__':
    unittest.main()
