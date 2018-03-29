
import unittest

import os
from contextlib import redirect_stdout
from io import StringIO

from i2b2model.testingutils.script_test_base import ScriptTestBase
from i2fhirb2 import __version__

from i2fhirb2.generate_i2b2 import generate_i2b2


class GenerateI2B2TestCase(ScriptTestBase):
    dirname = os.path.abspath(os.path.dirname(__file__))
    version = __version__

    @classmethod
    def setUpClass(cls):
        cls.dirname = os.path.split(os.path.abspath(__file__))[0]
        cls.save_output = False
        cls.tst_dir = "generatei2b2"
        cls.tst_fcn = generate_i2b2
        cls.conf_file_loc = "--conf {}".format(os.path.join(cls.dirname, 'data', 'db_conf'))

    def test_no_args(self):
        self.check_output_output("", "noargs")

    def test_help(self):
        self.check_output_output("-h", "help", exception=True)

    def test_version(self):
        self.check_output_output("-v", "version", exception=True)

    def test_list(self):
        # Make sure we have the basic files -- that everything in list is in our list. There may be more, however
        output = StringIO()
        with redirect_stdout(output):
            generate_i2b2(("--list " + self.conf_file_loc).split())
        fullfilename = os.path.join(self.dirname, 'data_out', self.tst_dir, "list")
        output_list_lines = output.getvalue().split('\n')
        with open(fullfilename) as list_f:
            list_f_lines = list_f.read().split('\n')
        for line in list_f_lines:
            if line not in output_list_lines:
                self.assertFalse(f"Missing file in db: {line}")

    def test_test(self):
        self.save_output = True
        self.check_output_output("--test " + self.conf_file_loc, "test", multipart_test=True)

    @unittest.skipIf(False, "Connection should not be possible with bad user/password")
    @unittest.expectedFailure
    def test_bad_test(self):
        bad_conf_file_loc = "--conf {}".format(os.path.join(self.dirname, 'data', 'db_conf_bad_password'))
        self.check_output_output("--test " + bad_conf_file_loc, "badtest", exception=True)


if __name__ == '__main__':
    unittest.main()
