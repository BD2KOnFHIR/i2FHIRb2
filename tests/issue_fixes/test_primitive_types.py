
import unittest


class PrimitiveIssueTestCase(unittest.TestCase):
    """ The fhir.ttl ontology has been updated and, among the fixes, the FHIR primitive types are now subclasses
    of FHIR.Primitive -- the current conversion tools are putting them in with a visual attribute of "DA"
    """
    def test_primitive(self):
        from i2fhirb2.fhir.fhirspecific import FHIR, is_primitive
        from tests.utils.shared_graph import shared_graph

        self.assertTrue(is_primitive(shared_graph, FHIR.string))
        self.assertFalse(is_primitive(shared_graph, FHIR.CodeableConcept))
        self.assertTrue(is_primitive(shared_graph, FHIR.uri))
        self.assertTrue(is_primitive(shared_graph, FHIR.index))
        self.assertTrue(is_primitive(shared_graph, FHIR.Reference))
        self.assertTrue(is_primitive(shared_graph, FHIR.code))
        self.assertFalse(is_primitive(shared_graph, FHIR.Observation))


if __name__ == '__main__':
    unittest.main()
