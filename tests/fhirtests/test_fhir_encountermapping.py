
import unittest

import datetime
from collections import OrderedDict

from dynprops import clear, as_dict
from i2b2model.shared.i2b2core import I2B2Core

from tests.utils.crc_testcase import CRCTestCase

from i2fhirb2.fhir.fhirencountermapping import EncounterNumberGenerator
from i2fhirb2.fhir.fhirspecific import FHIR
from i2fhirb2.common_cli_parameters import IDE_SOURCE_HIVE
from tests.utils.connection_helper import connection_helper


class FHIREncounterMappingTestCase(CRCTestCase):

    def test_basic_mapping(self):
        """ Test the basic encounter mapping entry

        Process:
        1) Prime the EncounterMapping tables
        2) Generate a simple FHIR EncounterMapping entry and verify that two
           entries are generated - one for the number to external IDE and a second
           for the HIVE ide
        """
        from i2fhirb2.fhir.fhirencountermapping import FHIREncounterMapping
        from i2b2model.data.i2b2encountermapping import EncounterMapping

        I2B2Core.update_date = datetime.datetime(2017, 5, 25)
        clear(FHIREncounterMapping)           # reset number generators

        with self.sourcesystem_cd() as ss_cd:
            I2B2Core.sourcesystem_cd = ss_cd
            em = FHIREncounterMapping(FHIR["Patient/f001"], "patient01", "http://hl7.org/fhir")
            self.assertEqual(OrderedDict([
                 ('encounter_ide', 'Patient/f001'),
                 ('encounter_ide_source', 'http://hl7.org/fhir/'),
                 ('project_id', 'fhir'),
                 ('encounter_num', 500000),
                 ('patient_ide', 'patient01'),
                 ('patient_ide_source', 'http://hl7.org/fhir'),
                 ('encounter_ide_status', 'A'),
                 ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('sourcesystem_cd', self._sourcesystem_cd),
                 ('upload_id', None)]), as_dict(em.encounter_mapping_entries[0]))
            self.assertEqual(OrderedDict([
                 ('encounter_ide', '500000'),
                 ('encounter_ide_source', IDE_SOURCE_HIVE),
                 ('project_id', 'fhir'),
                 ('encounter_num', 500000),
                 ('patient_ide', 'patient01'),
                 ('patient_ide_source', 'http://hl7.org/fhir'),
                 ('encounter_ide_status', 'A'),
                 ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('sourcesystem_cd', self._sourcesystem_cd),
                 ('upload_id', None)]), as_dict(em.encounter_mapping_entries[1]))
            self.assertEqual(2, len(em.encounter_mapping_entries))
            self.assertEqual(500000, em.encounter_num)

    def test_encounternum_refresh(self):
        """ Test the EncounterNumberGenerator refresh function.
         Process:
         1) Create a couple of local (non-db) encounter numbers
         2) Do a refresh and show that the number gets set to something else
         3) Do a refresh ignoring an upload id and do the same
         """
        png = EncounterNumberGenerator(2000017)
        self.assertEqual(png.new_number(), 2000017)
        self.assertEqual(png.new_number(), 2000018)
        opts = connection_helper()
        png.refresh(opts.tables, None)
        print("Next encounter number: {}".format(png.new_number()))
        self.assertNotEqual(png.new_number(), 2000019)
        png.refresh(opts.tables, 4321)
        self.assertNotEqual(png.new_number(), 2000019)


if __name__ == '__main__':
    unittest.main()
