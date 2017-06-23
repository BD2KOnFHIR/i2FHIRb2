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
from collections import OrderedDict
from datetime import datetime

from rdflib import Graph

from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFactFactory
from i2fhirb2.fhir.fhirspecific import FHIR
from tests.base_test_case import FHIRGraph

bmi_graph = "http://build.fhir.org/observation-example-bmi.ttl"


class ObservationFactTestCase(unittest.TestCase):
    g = None            # type: Graph

    @classmethod
    def setUpClass(cls):
        cls.g = FHIRGraph()
        cls.g.parse(bmi_graph, format="turtle")

    def test_basics(self):
        from i2fhirb2.i2b2model.i2b2observationfact import ObservationFact, ObservationFactKey
        ObservationFact.update_date = datetime(2017, 2, 19, 12, 33)
        ofk = ObservationFactKey(12345, 23456, 'provider', datetime(2017, 5, 23, 11, 17))
        x = ObservationFact(ofk, 'fhir:concept', sourcesystem_cd="FHIR STU3")
        self.assertEqual('encounter_num\tpatient_num\tconcept_cd\tprovider_id\tstart_date\tmodifier_cd\tinstance_num\t'
                         'valtype_cd\ttval_char\tnval_num\tvalueflag_cd\tquantity_num\tunits_cd\tend_date\t'
                         'location_cd\tobservation_blob\tconfidence_num\tupdate_date\tdownload_date\timport_date\t'
                         'sourcesystem_cd\tupload_id', x._header())
        self.assertEqual(OrderedDict([
             ('encounter_num', 23456),
             ('patient_num', 12345),
             ('concept_cd', 'fhir:concept'),
             ('provider_id', 'provider'),
             ('start_date', datetime(2017, 5, 23, 11, 17)),
             ('modifier_cd', '@'),
             ('instance_num', 1),
             ('valtype_cd', '@'),
             ('tval_char', None),
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
             ('sourcesystem_cd', 'FHIR STU3'),
             ('upload_id', None)]), x._freeze())

    def test_fhirobservationfact(self):
        from i2fhirb2.i2b2model.i2b2observationfact import ObservationFactKey
        from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact

        ofk = ObservationFactKey(12345, 23456, 'provider', datetime(2017, 5, 23, 11, 17))
        FHIRObservationFact.update_date = datetime(2017, 2, 19, 12, 33)
        FHIRObservationFact.sourcesystem_cd = "FHIR STU3"

        for subj in self.g.subjects(FHIR.nodeRole, FHIR.treeRoot):
            obj = self.g.value(subj, FHIR["Observation.status"])
            fof = FHIRObservationFact(self.g, ofk, FHIR["Observation.status"], obj)
            self.assertEqual(OrderedDict([
                 ('encounter_num', 23456),
                 ('patient_num', 12345),
                 ('concept_cd', 'FHIR:Observation.status'),
                 ('provider_id', 'provider'),
                 ('start_date', datetime(2017, 5, 23, 11, 17)),
                 ('modifier_cd', '@'),
                 ('instance_num', 1),
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
                 ('sourcesystem_cd', 'FHIR STU3'),
                 ('upload_id', None)]), fof._freeze())

    def test_complete_fact_list(self):
        from i2fhirb2.i2b2model.i2b2observationfact import ObservationFactKey
        from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact

        ofk = ObservationFactKey(1000000133, 471882, 'LCS-I2B2:D000109100', datetime(2017, 5, 23, 11, 17))
        FHIRObservationFact.update_date = datetime(2017, 2, 19, 12, 33)
        FHIRObservationFact.sourcesystem_cd = "FHIR STU3"
        oflist = FHIRObservationFactFactory(self.g, ofk, None)

        for ofle in oflist.facts:
            print(repr(ofle))
        with open('data_out/fhir_observation_fact.tsv', 'w') as outf:
            outf.write(FHIRObservationFact._header() + '\n')
            for e in oflist.facts:
                outf.write(repr(e) + '\n')


if __name__ == '__main__':
    unittest.main()
