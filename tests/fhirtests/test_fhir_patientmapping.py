
import unittest
from collections import OrderedDict
from datetime import datetime

from i2b2model.shared.i2b2core import I2B2Core, I2B2CoreWithUploadId
from dynprops import as_dict

from tests.utils.crc_testcase import CRCTestCase

from i2fhirb2.fhir.fhirpatientmapping import PatientNumberGenerator
from tests.utils.connection_helper import connection_helper


class FHIRPatientMappingTestCase(CRCTestCase):

    def test_patient_mapping(self):
        from i2fhirb2.fhir.fhirpatientmapping import FHIRPatientMapping

        I2B2Core.update_date = datetime(2017, 5, 25)
        I2B2CoreWithUploadId.upload_id = 1773486

        FHIRPatientMapping._clear()

        with self.sourcesystem_cd():
            I2B2Core.sourcesystem_cd = self._sourcesystem_cd
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
                 ('sourcesystem_cd', self._sourcesystem_cd),
                 ('upload_id', 1773486)]), as_dict(pm.patient_mapping_entries[0]))
            self.assertEqual(OrderedDict([
                 ('patient_ide', '100000001'),
                 ('patient_ide_source', 'HIVE'),
                 ('patient_num', 100000001),
                 ('patient_ide_status', 'A'),
                 ('project_id', 'fhir'),
                 ('update_date', datetime(2017, 5, 25, 0, 0)),
                 ('download_date', datetime(2017, 5, 25, 0, 0)),
                 ('import_date', datetime(2017, 5, 25, 0, 0)),
                 ('sourcesystem_cd', self._sourcesystem_cd),
                 ('upload_id', 1773486)]), as_dict(pm.patient_mapping_entries[1]))
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
