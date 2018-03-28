import os

from i2b2model.testingutils.crc_testcasebase import CRCTestCaseBase


class CRCTestCase(CRCTestCaseBase):
    test_prefix = "test_i2FHIRb2_"
    test_directory = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    test_conf_directory = os.path.join(test_directory, '..', 'conf')
    test_conf_file = os.path.abspath(os.path.join(test_conf_directory, 'db_conf'))