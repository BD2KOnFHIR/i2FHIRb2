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
import os
import unittest
from collections import OrderedDict
from datetime import datetime

from dynprops import heading, row, as_dict
from i2b2model.shared.i2b2core import I2B2Core, I2B2CoreWithUploadId

from tests.utils.crc_testcase import CRCTestCase
from rdflib import Graph

from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFactFactory
from i2fhirb2.fhir.fhirspecific import FHIR
from tests.utils.fhir_graph import FHIRGraph

bmi_graph = "http://build.fhir.org/observation-example-bmi.ttl"


class FHIRObservationFactTestCase(CRCTestCase):
    g = None            # type: Graph

    @classmethod
    def setUpClass(cls):
        cls.g = FHIRGraph()
        cls.g.parse(bmi_graph, format="turtle")

    def test_fhirobservationfact(self):
        from i2b2model.data.i2b2observationfact import ObservationFactKey
        from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact

        ofk = ObservationFactKey(12345, 23456, 'provider', datetime(2017, 5, 23, 11, 17))
        I2B2Core.update_date = datetime(2017, 2, 19, 12, 33)
        with self.sourcesystem_cd():
            I2B2Core.sourcesystem_cd = self._sourcesystem_cd
            I2B2CoreWithUploadId.upload_id = self._upload_id

            for subj in self.g.subjects(FHIR.nodeRole, FHIR.treeRoot):
                obj = self.g.value(subj, FHIR.Observation.status)
                fof = FHIRObservationFact(self.g, ofk, FHIR.Observation.status, None, obj)
                self.assertEqual(OrderedDict([
                     ('encounter_num', 23456),
                     ('patient_num', 12345),
                     ('concept_cd', 'FHIR:Observation.status'),
                     ('provider_id', 'provider'),
                     ('start_date', datetime(2017, 5, 23, 11, 17)),
                     ('modifier_cd', '@'),
                     ('instance_num', 0),
                     ('valtype_cd', 'T'),
                     ('tval_char', 'final'),
                     ('nval_num', None),
                     ('valueflag_cd', None),
                     ('quantity_num', None),
                     ('units_cd', None),
                     ('end_date', None),
                     ('location_cd', None),
                     ('observation_blob', None),
                     ('confidence_num', None),
                     ('update_date', datetime(2017, 2, 19, 12, 33)),
                     ('download_date', datetime(2017, 2, 19, 12, 33)),
                     ('import_date', datetime(2017, 2, 19, 12, 33)),
                     ('sourcesystem_cd', self._sourcesystem_cd),
                     ('upload_id', self._upload_id)]), as_dict(fof))

    def test_complete_fact_list(self):
        from i2b2model.data.i2b2observationfact import ObservationFactKey
        from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact

        filedir = os.path.split(os.path.abspath(__file__))[0]
        # Set this to true when generating new test data
        write_test_data = False
        ofk = ObservationFactKey(1000000133, 471882, 'LCS-I2B2:D000109100', datetime(2017, 5, 23, 11, 17))

        I2B2Core.update_date = datetime(2017, 2, 19, 12, 33)
        with self.sourcesystem_cd():
            I2B2Core.sourcesystem_cd = self._sourcesystem_cd
            I2B2CoreWithUploadId.upload_id = self._upload_id
            oflist = FHIRObservationFactFactory(self.g, ofk, None)

            test_fname = os.path.join(filedir, 'data', 'test_complete_fact_list.tsv')
            if write_test_data:
                with open(test_fname, 'w') as outf:
                    outf.write(heading(FHIRObservationFact) + '\n')
                    for e in sorted(oflist.observation_facts):
                        outf.write(row(e) + '\n')
            else:
                self.maxDiff = None
                with open(test_fname) as inf:
                    line_no = 1
                    self.assertEqual(heading(FHIRObservationFact), inf.readline().strip(), "Header mismatch")
                    for e in sorted(oflist.observation_facts):
                        line_no += 1
                        self.assertEqual(inf.readline()[:-1], row(e), "Line number {}".format(line_no))
                    self.assertEqual('', inf.read(1))
            self.assertFalse(write_test_data, "Creating a new test file always fails")


if __name__ == '__main__':
    unittest.main()
