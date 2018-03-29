
import unittest
import os

from fhirtordf.rdfsupport.namespaces import FHIR

from i2fhirb2.fhir.fhirmetadatavocabulary import FMVGraphNode
from i2fhirb2.fhir.fhirontologytable import FHIROntologyTable
from i2fhirb2.fhir.fhirw5ontology import FHIRW5Ontology
from tests.utils.shared_graph import shared_graph

save_output = False


class FHIROntologyP2TestCase(unittest.TestCase):
    output_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'data')

    def test_w5_graph(self):
        w5_ont = FHIRW5Ontology(shared_graph)
        test_file = os.path.join(self.output_dir, 'w5_graph.txt')
        if save_output:
            with open(test_file, 'w') as f:
                f.write(str(w5_ont))

        self.maxDiff = None
        with open(test_file) as f:
            self.assertEqual(f.read(), str(w5_ont))
        self.assertFalse(save_output, "Test always fails if save_output is true")

    def test_fhir_resource_concepts(self):
        fhir_ont = FHIROntologyTable(shared_graph)
        test_file = os.path.join(self.output_dir, 'fhir_resource_concepts.txt')
        test_data = '\n'.join(sorted([str(x) for x in fhir_ont.fhir_resource_concepts()]))
        if save_output:
            with open(test_file, 'w') as f:
                f.write(test_data)

        self.maxDiff = None
        with open(test_file) as f:
            self.assertEqual(f.read(), test_data)
        self.assertFalse(save_output, "Test always fails if save_output is true")

    def test_resource_graph(self):
        fhir_ont = FHIROntologyTable(shared_graph)
        test_file = os.path.join(self.output_dir, 'fhir_observation_resource_graph.txt')
        fmv_rg = FMVGraphNode(fhir_ont.graph, FHIR.Observation)
        if save_output:
            with open(test_file, 'w') as f:
                f.write(str(fmv_rg))

        self.maxDiff = None
        with open(test_file) as f:
            self.assertEqual(f.read(), str(fmv_rg))
        self.assertFalse(save_output, "Test always fails if save_output is true")


if __name__ == '__main__':
    unittest.main()
