# Copyright (c) 2018, Mayo Clinic
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
from datetime import datetime

import os
from fhirtordf.rdfsupport.namespaces import FHIR
from rdflib import Graph, URIRef

from i2fhirb2.fhir.fhircodemapping import value_string, value_quantity, value_integer, value_processors, \
    proc_value_node, value_codeable_concept
from i2fhirb2.i2b2model.data.i2b2observationfact import ObservationFact, valuetype_text, valuetype_number


class CodeMappingTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'data', 'codemapping')

    def setUp(self):
        from i2fhirb2.i2b2model.data.i2b2observationfact import ObservationFact, ObservationFactKey
        ObservationFact._clear()
        ObservationFact.update_date = datetime(2017, 2, 19, 12, 33)
        # Patient / provider / encounter / start date
        self.ofk = ObservationFactKey(12345, 23456, 'provider', datetime(2017, 5, 23, 11, 17))
        
        self.g = Graph()

    def test_value_string(self):
        self.g.parse(os.path.join(self.test_dir, 'observation-example-eye-color.ttl'), format="turtle")
        s = URIRef("http://hl7.org/fhir/Observation/eye-color")
        sval = self.g.value(s, FHIR.Observation.valueString)
        vs = value_string(self.g, sval, ObservationFact(self.ofk, FHIR.string))
        self.assertEqual(valuetype_text.code, vs.valtype_cd)
        self.assertEqual("blue", vs.tval_char)
        vs2 = proc_value_node(self.g, ObservationFact(self.ofk, FHIR.string), FHIR.Observation.valueString, sval)
        self.assertEqual("blue", vs2.tval_char)

    def test_value_quantity(self):
        self.g.parse(os.path.join(self.test_dir, 'observation-example-f204-creatinine.ttl'), format="turtle")
        s = URIRef("http://hl7.org/fhir/Observation/f204")
        qval = self.g.value(s, FHIR.Observation.valueQuantity)
        vs = value_quantity(self.g, qval, ObservationFact(self.ofk, FHIR.SimpleQuantity))
        self.assertEqual(valuetype_number.code, vs.valtype_cd)
        self.assertEqual('E', vs.tval_char)
        self.assertEqual(122, vs.nval_num)
        self.assertEqual('umol/L', vs.units_cd)

        self.g.parse(os.path.join(self.test_dir, 'diagnosticreport-micro1.ttl'), format="turtle")
        # >
        s = URIRef("https://example.com/base/Observation/obx2-2")
        qval = self.g.value(s, FHIR.Observation.valueQuantity)
        vs = value_quantity(self.g, qval, ObservationFact(self.ofk, FHIR.SimpleQuantity))
        self.assertEqual('G', vs.tval_char)
        self.assertEqual(2, vs.nval_num)
        self.assertIsNone(vs.units_cd)
        # >=
        s = URIRef("https://example.com/base/Observation/obx2-4")
        qval = self.g.value(s, FHIR.Observation.valueQuantity)
        vs = value_quantity(self.g, qval, ObservationFact(self.ofk, FHIR.SimpleQuantity))
        self.assertEqual('GE', vs.tval_char)
        self.assertEqual(4, vs.nval_num)
        self.assertIsNone(vs.units_cd)
        # <
        s = URIRef("https://example.com/base/Observation/obx2-6")
        qval = self.g.value(s, FHIR.Observation.valueQuantity)
        vs = value_quantity(self.g, qval, ObservationFact(self.ofk, FHIR.SimpleQuantity))
        self.assertEqual('L', vs.tval_char)
        self.assertEqual(0.5, vs.nval_num)
        self.assertIsNone(vs.units_cd)
        # <
        s = URIRef("https://example.com/base/Observation/obx2-8")
        qval = self.g.value(s, FHIR.Observation.valueQuantity)
        vs = value_quantity(self.g, qval, ObservationFact(self.ofk, FHIR.SimpleQuantity))
        self.assertEqual('LE', vs.tval_char)
        self.assertEqual(1, vs.nval_num)
        self.assertIsNone(vs.units_cd)
        # Dispatch test
        vs2 = proc_value_node(self.g, ObservationFact(self.ofk, FHIR.string), FHIR.Observation.valueQuantity, qval)
        self.assertEqual(1, vs2.nval_num)

    def test_value_integer(self):
        self.g.parse(os.path.join(self.test_dir, 'diagnosticreport-micro1.ttl'), format="turtle")
        s = URIRef("https://example.com/base/Observation/obx2-10")
        qval = self.g.value(s, FHIR.Observation.valueInteger)
        vs = value_integer(self.g, qval, ObservationFact(self.ofk, FHIR.integer))
        self.assertEqual('E', vs.tval_char)
        self.assertEqual(-17243, vs.nval_num)
        self.assertIsNone(vs.units_cd)
        # Dispatch test
        vs2 = proc_value_node(self.g, ObservationFact(self.ofk, FHIR.string), FHIR.Observation.valueInteger, qval)
        self.assertEqual(-17243, vs2.nval_num)

    def test_value_codeable_concept_1(self):
        self.g.parse(os.path.join(self.test_dir, 'diagnosticreport-micro1.ttl'), format="turtle")
        s = URIRef("https://example.com/base/Observation/obx1-4")
        cval = self.g.value(s, FHIR.Observation.valueCodeableConcept)
        vs = value_codeable_concept(self.g, cval, ObservationFact(self.ofk, FHIR.CodeableConcept))[0]
        self.assertEqual(valuetype_text.code, vs.valtype_cd)
        self.assertEqual("Staphylococcus aureus", vs.tval_char)
        self.assertEqual("@", vs.modifier_cd)

    def test_value_codeable_concept_2(self):
        self.g.parse(os.path.join(self.test_dir, 'observation-example-2minute-apgar-score.ttl'), format="turtle")
        s = URIRef("http://hl7.org/fhir/Observation/2minute-apgar-score")
        found = False
        for v in self.g.objects(s, FHIR.Observation.component):
            if self.g.value(v, FHIR.index).value == 0:
                found = True
                cval = self.g.value(v, FHIR.Observation.component.valueCodeableConcept, any=False)
                for vs in value_codeable_concept(self.g, cval, ObservationFact(self.ofk, FHIR.CodeableConcept)):
                    self.assertEqual(valuetype_text.code, vs.valtype_cd)
                    self.assertEqual("1. Good color in body with bluish hands or feet", vs.tval_char)
                    self.assertEqual("LOINC:LA6723-6", vs.modifier_cd)
                    from pprint import PrettyPrinter; pp = PrettyPrinter().pprint
                    pp(vs._freeze())
        
        self.assertTrue(found)




if __name__ == '__main__':
    unittest.main()
