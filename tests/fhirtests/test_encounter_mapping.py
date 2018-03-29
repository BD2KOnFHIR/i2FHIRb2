
import unittest
from collections import OrderedDict
from datetime import datetime

from dynprops import clear, as_dict
from i2b2model.data.i2b2encountermapping import EncounterMapping
from i2b2model.shared.i2b2core import I2B2Core, I2B2CoreWithUploadId


class EncounterMappingTestCase(unittest.TestCase):

    def tearDown(self):
        clear(EncounterMapping)

    def test_encounter_mapping(self):
        """ Test i2b2 EncounterMapping resource

        :return:
        """
        from i2b2model.data.i2b2encountermapping import EncounterIDEStatus

        clear(EncounterMapping)
        I2B2Core.update_date = datetime(2017, 5, 25)
        I2B2Core.sourcesystem_cd = "FHIR"
        I2B2CoreWithUploadId.upload_id = 7774468

        em = EncounterMapping("f001", "http://hl7.org/fhir", "FHIR", 5000017, "patient01",
                              "http://hl7.org/fhir", EncounterIDEStatus.active)

        self.assertEqual(OrderedDict([
             ('encounter_ide', 'f001'),
             ('encounter_ide_source', 'http://hl7.org/fhir'),
             ('project_id', 'FHIR'),
             ('encounter_num', 5000017),
             ('patient_ide', 'patient01'),
             ('patient_ide_source', 'http://hl7.org/fhir'),
             ('encounter_ide_status', 'A'),
             ('update_date', datetime(2017, 5, 25, 0, 0)),
             ('download_date', datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', 7774468)]), as_dict(em))


if __name__ == '__main__':
    unittest.main()
