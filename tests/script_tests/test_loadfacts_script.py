
import unittest

import os

from i2b2model.testingutils.script_test_base import ScriptTestBase
from i2fhirb2 import __version__

from i2fhirb2.loadfacts import load_facts


class LoadFactsTestCase(ScriptTestBase):
    dirname = os.path.abspath(os.path.dirname(__file__))
    version = __version__

    @classmethod
    def setUpClass(cls):
        cls.dirname = os.path.split(os.path.abspath(__file__))[0]
        cls.save_output = False
        cls.tst_dir = "loadfacts"
        cls.tst_fcn = load_facts

    def test_no_args(self):
        self.check_error_output("", "noargs")

    def test_no_input(self):
        self.check_error_output("-l", "noinput")

    def test_help(self):
        self.check_output_output("-h", "help", exception=True)


if __name__ == '__main__':
    unittest.main()
