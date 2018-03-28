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
from contextlib import contextmanager, redirect_stdout
from datetime import datetime

import os
from io import StringIO

from dynprops import clear
from fhirtordf.rdfsupport.namespaces import FHIR
from i2b2model.shared.i2b2core import I2B2Core
from rdflib import Graph, URIRef

from i2fhirb2.fhir.fhircodemapping import value_string, value_quantity, value_integer, value_processors, \
    proc_value_node, value_codeable_concept
from i2b2model.data.i2b2observationfact import ObservationFact, valuetype_text, valuetype_number


# Note: while less than an ideal architecture, the current value conversion model takes a single observation fact
#       as an input and stores the appropriate value into it.  In the case (coding, primarily) that a single FHIR
#       value produces multiple observation facts, the first fact will be the argument and the subsequent facts
#       will be in the return value.  Thus, if you have to facts from one value, you would get one in the passed
#       fact and the second as a return value.
from tests.utils.fhir_graph import test_data_directory


class CodeMappingTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'data', 'codemapping')

    def setUp(self):
        from i2b2model.data.i2b2observationfact import ObservationFact, ObservationFactKey
        clear(ObservationFact)
        I2B2Core.update_date = datetime(2017, 2, 19, 12, 33)
        # Patient / provider / encounter / start date
        self.ofk = ObservationFactKey(12345, 23456, 'provider', datetime(2017, 5, 23, 11, 17))
        
        self.g = Graph()

    def test_value_string(self):
        self.g.parse(os.path.join(self.test_dir, 'observation-example-eye-color.ttl'), format="turtle")
        obsf = ObservationFact(self.ofk, FHIR.string)
        s = URIRef("http://hl7.org/fhir/Observation/eye-color")
        sval = self.g.value(s, FHIR.Observation.valueString)
        vs = value_string(self.g, sval, obsf)
        self.assertEqual(0, len(vs))
        self.assertEqual(valuetype_text.code, obsf.valtype_cd)
        self.assertEqual("blue", obsf.tval_char)

        obsf = ObservationFact(self.ofk, FHIR.string)
        vs2 = proc_value_node(self.g, obsf, FHIR.Observation.valueString, sval)
        self.assertEqual(0, len(vs2))
        self.assertEqual("blue", obsf.tval_char)

    def test_value_quantity_units(self):
        self.g.parse(os.path.join(self.test_dir, 'observation-example-f204-creatinine-unit2.ttl'), format="turtle")
        s = URIRef("http://hl7.org/fhir/Observation/f204")

        # Units present
        obsf = ObservationFact(self.ofk, FHIR.SimpleQuantity)
        qval = self.g.value(s, FHIR.Observation.valueQuantity1)
        value_quantity(self.g, qval, obsf)
        self.assertEqual('umol/L', obsf.units_cd)

        # System/code
        obsf = ObservationFact(self.ofk, FHIR.SimpleQuantity)
        qval = self.g.value(s, FHIR.Observation.valueQuantity2)
        value_quantity(self.g, qval, obsf)
        self.assertEqual('SCT:258814008', obsf.units_cd)

        obsf = ObservationFact(self.ofk, FHIR.SimpleQuantity)
        qval = self.g.value(s, FHIR.Observation.valueQuantity3)
        value_quantity(self.g, qval, obsf)
        self.assertEqual('GPF', obsf.units_cd)

        # No units at all
        obsf = ObservationFact(self.ofk, FHIR.SimpleQuantity)
        qval = self.g.value(s, FHIR.Observation.valueQuantity4)
        value_quantity(self.g, qval, obsf)
        self.assertIsNone(obsf.units_cd)

    def test_value_quantity(self):
        self.g.parse(os.path.join(self.test_dir, 'observation-example-f204-creatinine.ttl'), format="turtle")
        obsf = ObservationFact(self.ofk, FHIR.SimpleQuantity)
        s = URIRef("http://hl7.org/fhir/Observation/f204")
        qval = self.g.value(s, FHIR.Observation.valueQuantity)
        vs = value_quantity(self.g, qval, obsf)
        self.assertEqual(0, len(vs))
        self.assertEqual(valuetype_number.code, obsf.valtype_cd)
        self.assertEqual('E', obsf.tval_char)
        self.assertEqual(122, obsf.nval_num)
        self.assertEqual('umol/L', obsf.units_cd)

        # Test '>'
        self.g.parse(os.path.join(self.test_dir, 'diagnosticreport-micro1.ttl'), format="turtle")
        obsf = ObservationFact(self.ofk, FHIR.SimpleQuantity)
        s = URIRef("https://example.com/base/Observation/obx2-2")
        qval = self.g.value(s, FHIR.Observation.valueQuantity)
        vs = value_quantity(self.g, qval, obsf)
        self.assertEqual(0, len(vs))
        self.assertEqual('G', obsf.tval_char)
        self.assertEqual(2, obsf.nval_num)
        self.assertIsNone(obsf.units_cd)

        # Test '>='
        s = URIRef("https://example.com/base/Observation/obx2-4")
        obsf = ObservationFact(self.ofk, FHIR.SimpleQuantity)
        qval = self.g.value(s, FHIR.Observation.valueQuantity)
        vs = value_quantity(self.g, qval, obsf)
        self.assertEqual(0, len(vs))
        self.assertEqual('GE', obsf.tval_char)
        self.assertEqual(4, obsf.nval_num)
        self.assertIsNone(obsf.units_cd)

        # Test '<'
        s = URIRef("https://example.com/base/Observation/obx2-6")
        obsf = ObservationFact(self.ofk, FHIR.SimpleQuantity)
        qval = self.g.value(s, FHIR.Observation.valueQuantity)
        vs = value_quantity(self.g, qval, obsf)
        self.assertEqual(0, len(vs))
        self.assertEqual('L', obsf.tval_char)
        self.assertEqual(0.5, obsf.nval_num)
        self.assertIsNone(obsf.units_cd)

        # Test '<;
        s = URIRef("https://example.com/base/Observation/obx2-8")
        obsf = ObservationFact(self.ofk, FHIR.SimpleQuantity)
        qval = self.g.value(s, FHIR.Observation.valueQuantity)
        vs = value_quantity(self.g, qval, obsf)
        self.assertEqual(0, len(vs))
        self.assertEqual('LE', obsf.tval_char)
        self.assertEqual(1, obsf.nval_num)
        self.assertIsNone(obsf.units_cd)

        # Dispatch test
        obsf = ObservationFact(self.ofk, FHIR.string)
        vs2 = proc_value_node(self.g, obsf, FHIR.Observation.valueQuantity, qval)
        self.assertEqual(0, len(vs2))
        self.assertEqual(1, obsf.nval_num)

    def test_value_integer(self):
        self.g.parse(os.path.join(self.test_dir, 'diagnosticreport-micro1.ttl'), format="turtle")
        s = URIRef("https://example.com/base/Observation/obx2-10")
        obsf = ObservationFact(self.ofk, FHIR.integer)
        qval = self.g.value(s, FHIR.Observation.valueInteger)
        vs = value_integer(self.g, qval, obsf)
        self.assertEqual(0, len(vs))
        self.assertEqual('E', obsf.tval_char)
        self.assertEqual(-17243, obsf.nval_num)
        self.assertIsNone(obsf.units_cd)
        # Dispatch test
        obsf = ObservationFact(self.ofk, FHIR.string)
        vs2 = proc_value_node(self.g, obsf, FHIR.Observation.valueInteger, qval)
        self.assertEqual(-17243, obsf.nval_num)

    def test_value_codeable_concept_1(self):
        self.g.parse(os.path.join(self.test_dir, 'diagnosticreport-micro1.ttl'), format="turtle")
        s = URIRef("https://example.com/base/Observation/obx1-4")
        obsf = ObservationFact(self.ofk, FHIR.CodeableConcept)
        cval = self.g.value(s, FHIR.Observation.valueCodeableConcept)
        vs = value_codeable_concept(self.g, cval, obsf)
        self.assertEqual(0, len(vs))
        self.assertEqual(valuetype_text.code, obsf.valtype_cd)
        self.assertEqual("Staphylococcus aureus", obsf.tval_char)
        self.assertEqual("@", obsf.modifier_cd)

    def test_value_codeable_concept_2(self):
        self.g.parse(os.path.join(self.test_dir, 'observation-example-2minute-apgar-score.ttl'), format="turtle")
        s = URIRef("http://hl7.org/fhir/Observation/2minute-apgar-score")
        found = False
        for v in self.g.objects(s, FHIR.Observation.component):
            if self.g.value(v, FHIR.index).value == 0:
                found = True
                cval = self.g.value(v, FHIR.Observation.component.valueCodeableConcept, any=False)
                obsf = ObservationFact(self.ofk, FHIR.CodeableConcept)
                output_buffer = StringIO()
                with redirect_stdout(output_buffer):
                    addl_facts = value_codeable_concept(self.g, cval, obsf)
                self.assertTrue('Unrecognized namespace: http:/acme.ped/apgarcolor/' in output_buffer.getvalue())

                self.assertEqual(valuetype_text.code, obsf.valtype_cd)
                self.assertEqual('1. Good color in body with bluish hands or feet', obsf.tval_char)
                self.assertEqual('@', obsf.modifier_cd)

                self.assertEqual(1, len(addl_facts))
                obsf2 = addl_facts[0]

                self.assertEqual(valuetype_text.code, obsf2.valtype_cd)
                self.assertEqual("Good color in body with bluish hands or feet", obsf2.tval_char)
                self.assertEqual("LOINC:LA6723-6", obsf2.modifier_cd)

        self.assertTrue(found)


if __name__ == '__main__':
    unittest.main()
