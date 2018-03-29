
import unittest

import os

from tests.utils.fhir_graph import test_data_directory
from tests.utils.load_facts_helper import LoadFactsHelper


class MtConceptTestCase(LoadFactsHelper):
    caller_filename = __file__

    def test_mt_concept_code(self):
        """ Test for a problem encountered in SMARTONFHIR load where concept_cd was null """
        test_dir = os.path.join(test_data_directory, 'smartonfhir_testdata', 'samples')
        with self.sourcesystem_cd():
            self.load_named_resource('mt_concept_cd.json', test_dir)
        self.assertTrue(True)

    def test_loinc_concept_code(self):
        """ Test for a problem encountered in SMARTONFHIR load where concept_cd was null """
        test_dir = os.path.join(test_data_directory, 'smartonfhir_testdata', 'samples')
        with self.sourcesystem_cd():
            self.load_named_resource('obs_sample_1134281.ttl', test_dir)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
