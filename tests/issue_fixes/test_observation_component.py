# Copyright (c) 2017, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the Mayo Clinic nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest

import os
from _csv import QUOTE_NONE
from csv import DictReader
from typing import Dict

from i2fhirb2.loadfacts import load_facts
from tests.utils.fhir_graph import test_data_directory, test_conf_directory
from i2b2model.testingutils.base_test_case import make_and_clear_directory


class ObservationComponentTestCase(unittest.TestCase):
    dirname, _ = os.path.split(os.path.abspath(__file__))
    output_dir = os.path.abspath(os.path.join(dirname, 'data_out', 'test_observation_component'))

    def setUp(self):
        make_and_clear_directory(self.output_dir)

    def tearDown(self):
        make_and_clear_directory(self.output_dir)

    def create_test_output(self, infilename: str):
        mv = os.path.abspath(os.path.join(test_data_directory, 'fhir_metadata_vocabulary'))
        conf = os.path.abspath(os.path.join(test_conf_directory, 'db_conf'))
        input_file = os.path.abspath(os.path.join(self.dirname, 'data', infilename))
        load_facts("-mv {} --conf {} -i {} -t rdf -od {}".format(mv, conf, input_file, self.output_dir).split())

    def test_boyle(self):
        self.create_test_output('Boyle963_Kathleen891_83.ttl')
        with open(os.path.join(self.output_dir, 'observation_fact.tsv')) as output_tsv_file:
            rslt = DictReader(output_tsv_file, delimiter="\t", quoting=QUOTE_NONE)
            sbp_idx = dbp_idx = sbp_res_idx = dbp_res_idx = 0
            for row in rslt:
                if row['tval_char'] == '8462-4':
                    dbp_idx = row['instance_num']
                elif row['tval_char'] == '8480-6':
                    sbp_idx = row['instance_num']
                elif row['nval_num'] == '116':
                    dbp_res_idx = row['instance_num']
                elif row['nval_num'] == '172':
                    sbp_res_idx = row['instance_num']
        self.assertTrue(sbp_idx == sbp_res_idx and dbp_idx == dbp_res_idx and sbp_idx != dbp_idx)

    def test_issue_6(self):
        self.create_test_output('Boyle963_Kathleen891_83.ttl')
        with open(os.path.join(self.output_dir, 'observation_fact.tsv')) as output_tsv_file:
            rslt = DictReader(output_tsv_file, delimiter="\t", quoting=QUOTE_NONE)
            inst_codes = {}            # type: Dict[int, str]
            for row in rslt:
                # print('\t'.join((row['instance_num'], row['concept_cd'], row['modifier_cd'],
                #       row['tval_char'], row['nval_num'])))
                inst_num = int(row['instance_num'])
                if inst_num > 0:
                    if inst_num in inst_codes:
                        self.assertEqual(inst_codes[inst_num], row['concept_cd'])
                    else:
                        inst_codes[inst_num] = row['concept_cd']


if __name__ == '__main__':
    unittest.main()
