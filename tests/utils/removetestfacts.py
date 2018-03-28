
# Remove any facts that have been left as the result of unit tests.
#
#  This should be run before and after any unit tests until we get the SQL issue resolved

import os
import sys

from tests.utils.crc_testcase import test_conf_file, CRCTestCase

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.join(os.getcwd(), os.path.dirname(__file__)), '..'))
    from i2b2model.scripts.removefacts import remove_facts

    remove_facts(f"--conf {test_conf_file} -p {CRCTestCase.test_prefix} --removetestlist".split())
