
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
