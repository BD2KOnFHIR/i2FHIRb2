
import unittest

import os

from tests.utils.crc_testcase import CRCTestCase

from tests.utils.fhir_graph import test_data_directory, test_conf_directory

conf_file = os.path.join(test_conf_directory, 'db_conf')
med_desp_upload_id = 2020
pat_upload_id = 2021


class LoadFactsPatientDimensionTestCase(CRCTestCase):

    @unittest.skip
    def test1(self):
        from i2fhirb2.loadfacts import load_facts

        data_file = os.path.join(test_data_directory, 'medicationdispense0308.ttl')
        with self.sourcesystem_cd():
            load_facts(f"-i {data_file} -l --conf {conf_file} -u {med_desp_upload_id} -ss {self._sourcesystem_cd}".
                       split())
            self.assertEqual(True, False)

    @unittest.skip
    def test2(self):
        from i2fhirb2.loadfacts import load_facts

        data_file = "http://hl7.org/fhir/Patient/pat1"
        with self.sourcesystem_cd():
            load_facts(f"-i {data_file} -l --conf {conf_file} -u {pat_upload_id} -ss {self._sourcesystem_cd}".split())
            self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
