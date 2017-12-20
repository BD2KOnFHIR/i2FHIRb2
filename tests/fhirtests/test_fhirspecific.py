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

from fhirtordf.rdfsupport.namespaces import W5, FHIR
from rdflib import RDF

from i2fhirb2.fhir.fhirspecific import is_w5_uri, composite_uri, modifier_name, modifier_code, rightmost_element, \
    modifier_path, concept_name, concept_code
from tests.utils.shared_graph import shared_graph


class FHIRSpecificTestCase(unittest.TestCase):
    def test_is_w5_uri(self):
        self.assertTrue(is_w5_uri(W5.something))
        self.assertFalse(is_w5_uri(FHIR.something))

    def test_composite_uri(self):
        self.assertEqual(str(FHIR.Observation.status.code),
                         str(composite_uri(FHIR.Observation.status, FHIR.CodedElement.code)))
        self.assertEqual(str(FHIR.Observation.code),
                         str(composite_uri(FHIR.Observation, FHIR.CodedElement.code)))
        self.assertEqual(str(FHIR.Observation.x.y.t),
                         str(composite_uri(FHIR.Observation.x.y, FHIR.Element.a.b.z.t)))

    def test_modifier_name(self):
        g = shared_graph
        self.assertEqual("text", modifier_name(g, FHIR.Quantity.text))
        self.assertEqual("destination profile", modifier_name(g, FHIR.TestScript.destination.profile))

    def test_modifier_code(self):
        self.assertEqual("FHIR:TestScript.destination.profile", modifier_code(FHIR.TestScript.destination.profile))

    def test_rightmost_element(self):
        self.assertEqual('\\text\\', rightmost_element(FHIR.CodedEntry.code.text))
        self.assertEqual('\\', rightmost_element(FHIR.CodedEntry))

    def test_modifier_path(self):
        self.assertEqual('code\\text\\', modifier_path(FHIR.CodedEntry.code.text))
        self.assertEqual('code\\', modifier_path(FHIR.CodedEntry.code))
        self.assertEqual('CodedEntry\\', modifier_path(FHIR.CodedEntry))

    def test_concept_name(self):
        g = shared_graph
        self.assertEqual("FamilyMemberHistory condition onsetRange",
                         concept_name(g, FHIR.FamilyMemberHistory.condition.onsetRange))
        self.assertEqual("missing", concept_name(g, FHIR.missing))

    def test_concept_code(self):
        self.assertEqual("FHIR:CodedEntry", concept_code(FHIR.CodedEntry))
        self.assertEqual("W5:administrative", concept_code(W5.administrative))
        print(concept_code(RDF.type))


if __name__ == '__main__':
    unittest.main()
