import re
import unittest

import os
from functools import reduce

from i2b2model.testingutils.script_test_base import ScriptTestBase

from i2fhirb2.fhir.fhirencountermapping import FHIREncounterMapping
from i2fhirb2.fhir.fhirpatientmapping import FHIRPatientMapping
from tests.utils.crc_testcase import CRCTestCase


from i2fhirb2.loadfacts import load_facts
from tests.utils.fhir_graph import test_conf_file


class Issue8TestCase(ScriptTestBase, CRCTestCase):
    dirname = os.path.abspath(os.path.dirname(__file__))
    version = re.__version__

    enc_re = r'Starting encounter number: (\d+)'
    pat_re = r'Starting patient number: (\d+)'
    triples_re = r'\d+ triples'
    org_pat = r'\d+.*\(Organization\).*'
    pat_pat = r'\d+.*\(Patient\).*'
    obs_pat = r'\d+.*\(Observation\).*'
    file_pat = r'loading .*'
    del_patterns = [enc_re, pat_re, triples_re, org_pat, pat_pat, obs_pat, file_pat]

    @classmethod
    def setUpClass(cls):
        cls.dirname = os.path.split(os.path.abspath(__file__))[0]
        cls.save_output = False
        cls.tst_dir = "issue8"
        cls.tst_fcn = load_facts
        FHIRPatientMapping._clear()
        FHIREncounterMapping._clear()

    def test_patient_dimension_issue(self):
        datadir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
        fileloc = os.path.join(datadir, 'patient-example.json')
        with self.sourcesystem_cd():
            argstr = f"--conf {test_conf_file} -l -t json -u {self._upload_id} " \
                     f"--sourcesystem {self._sourcesystem_cd} -i {fileloc}"
            self.check_filtered_output(argstr, "first_load", self._filter_results)
            first_enc_num = self._start_enc_number      # No encounter (visit) numbers are generated in this test
            first_pat_num = self._start_pat_num + 1

            self.check_filtered_output(argstr, "second_load", self._filter_results)
            self.assertEqual(first_enc_num, self._start_enc_number)
            self.assertEqual(first_pat_num, self._start_pat_num)

            self.check_filtered_output(argstr, "third_load", self._filter_results)
            self.assertEqual(first_enc_num, self._start_enc_number)
            self.assertEqual(first_pat_num, self._start_pat_num)

            # Now add an encounter and make sure things still work out
            fileloc = os.path.join(datadir, 'observation-example-bmi.json')
            argstr = f"--conf {test_conf_file} -l -t json -u {self._upload_id} " \
                     f"--sourcesystem {self._sourcesystem_cd} -i {fileloc}"
            self.check_filtered_output(argstr, "obs_load", self._filter_results)
            self.assertEqual(first_enc_num, self._start_enc_number)
            self.assertEqual(first_pat_num, self._start_pat_num)

    def _filter_results(self, inp: str) -> str:
        self._start_enc_number = int(re.search(r'Starting encounter number: (\d+)', inp).groups()[0])
        self._start_pat_num = int(re.search(r'Starting patient number: (\d+)', inp).groups()[0])
        return reduce(lambda txt, p: re.sub(p, '', txt), self.del_patterns, inp)


if __name__ == '__main__':
    unittest.main()
