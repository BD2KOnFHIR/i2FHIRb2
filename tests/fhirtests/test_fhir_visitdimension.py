import os
import unittest

import datetime
from collections import OrderedDict

from i2b2model.shared.i2b2core import I2B2Core, I2B2CoreWithUploadId

from tests.utils.crc_testcase import CRCTestCase
from isodate import FixedOffset
from rdflib import Graph, Literal, XSD

from i2fhirb2.fhir.fhirencountermapping import FHIREncounterMapping
from dynprops import clear, as_dict


class FHIRVisitDimensionTestCase(CRCTestCase):

    def test_load_ttl(self):
        from i2fhirb2.fhir.fhirvisitdimension import FHIRVisitDimension
        from i2fhirb2.fhir.fhirspecific import FHIR
        from i2b2model.data.i2b2visitdimension import VisitDimension
        from i2b2model.data.i2b2encountermapping import EncounterMapping

        I2B2Core.update_date = datetime.datetime(2017, 5, 25)
        I2B2CoreWithUploadId.upload_id = 1700043

        clear(FHIREncounterMapping)           # reset the encounter number generator

        g = Graph()
        g.load(os.path.join(os.path.split(os.path.abspath(__file__))[0], "data",
                            "diagnosticreport-example-f202-bloodculture.ttl"), format="turtle")
        with self.sourcesystem_cd():
            I2B2Core.sourcesystem_cd = self._sourcesystem_cd
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
                 ('sourcesystem_cd', self._sourcesystem_cd),
                 ('upload_id', 1700043)]), as_dict(pd_entry.visit_dimension_entry))

            self.assertEqual(OrderedDict([
                 ('encounter_ide', 'DiagnosticReport/f202'),
                 ('encounter_ide_source', 'http://hl7.org/fhir/'),
                 ('project_id', 'fhir'),
                 ('encounter_num', 500000),
                 ('patient_ide', 'f201'),
                 ('patient_ide_source', 'http://hl7.org/fhir'),
                 ('encounter_ide_status', 'A'),
                 ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('sourcesystem_cd', self._sourcesystem_cd),
                 ('upload_id', 1700043)]), as_dict(pd_entry.encounter_mappings.encounter_mapping_entries[0]))
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
                 ('sourcesystem_cd', self._sourcesystem_cd),
                 ('upload_id', 1700043)]), as_dict(pd_entry.encounter_mappings.encounter_mapping_entries[1]))
            self.assertEqual(2, len(pd_entry.encounter_mappings.encounter_mapping_entries))


if __name__ == '__main__':
    unittest.main()
