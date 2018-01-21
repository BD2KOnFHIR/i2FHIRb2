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
