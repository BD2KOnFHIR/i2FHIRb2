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
from datetime import datetime
from typing import List, Tuple

from i2fhirb2.fhir.fhirspecific import FHIR
from i2fhirb2.i2b2model.metadata.i2b2conceptdimension import ConceptDimension
from i2fhirb2.i2b2model.metadata.i2b2modifierdimension import ModifierDimension
from i2fhirb2.i2b2model.metadata.i2b2ontology import OntologyRoot, OntologyEntry
from tests.utils.base_test_case import BaseTestCase
from tests.utils.shared_graph import shared_graph

# True means create the output file -- false means test it
create_output_files = False         # Be very careful when setting this to 'true'


class FHIROntologyTestCase(BaseTestCase):
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

    def setUp(self):
        from i2fhirb2.i2b2model.metadata import dimensionmetadata
        ref_datetime = datetime(2017, 5, 25, 13, 0)
        dimensionmetadata.creation_date = ref_datetime

        from i2fhirb2.i2b2model.metadata.i2b2ontology import OntologyEntry
        OntologyEntry._clear()
        OntologyEntry.sourcesystem_cd = "FHIR STU3"
        OntologyEntry.update_date = OntologyRoot.update_date = ref_datetime
        OntologyRoot.sourcesystem_cd = "FHIR STU3"

        from i2fhirb2.i2b2model.metadata.i2b2modifierdimension import ModifierDimension
        ModifierDimension._clear()
        ModifierDimension.sourcesystem_cd = "FHIR STU3"
        ModifierDimension.update_date = ref_datetime
        ModifierDimension.graph = shared_graph

        from i2fhirb2.i2b2model.metadata.i2b2conceptdimension import ConceptDimension
        ConceptDimension._clear()
        ConceptDimension.sourcesystem_cd = "FHIR STU3"
        ConceptDimension.update_date = ConceptDimension.import_date = ConceptDimension.download_date = \
            ref_datetime
        ConceptDimension.graph = shared_graph

    @staticmethod
    def esc_output(txt: str) -> str:
        return txt.replace('\r\n', '').replace('\r', '').replace('\n', '').strip('\t')

    def tst_dimension(self, header: str, dimension_entries: List, fname: str) -> None:
        """
        Test dimension entries against the supplied output file
        :param header: Expected header line
        :param dimension_entries: Dimension list
        :param fname: output file name base (no .tsv)
        """
        full_fname = os.path.join(FHIROntologyTestCase.output_dir, fname + '.tsv')
        if create_output_files:
            with open(full_fname, 'w') as outf:
                outf.write(header + '\n')
                for e in sorted(dimension_entries):
                    outf.write(self.esc_output(repr(e)) + '\n')
            self.maxDiff = None
            with open(full_fname, 'r') as outf:
                self.assertEqual(outf.readline().strip(), header, "Header mismatch")
                line_number = 1
                for e in sorted(dimension_entries):
                    line_number += 1
                    self.assertEqual(outf.readline().strip('\r\n\t'), self.esc_output(repr(e)),
                                     "Mismatch on line {}".format(line_number))
                self.assertEqual(outf.read(), "")

    def tst_output(self, dimensions: Tuple[List[OntologyEntry], List[ConceptDimension], List[ModifierDimension]],
                   resource_name: str) -> None:
        """
        Test the output of FHIROntologyTable.dimension_list as generated against resource
        :param dimensions: ontology, concept and modifier dimension entries
        :param resource_name: name of specific test file (e.g. 'observation', 'domain_resource', etc.)
        """
        self.tst_dimension(OntologyEntry._header(), dimensions[0], 'fhir_ontology_' + resource_name)
        self.tst_dimension(ConceptDimension._header(), dimensions[1], 'fhir_concept_dimension_' + resource_name)
        self.tst_dimension(ModifierDimension._header(), dimensions[2], 'fhir_modifier_dimension_' + resource_name)

    def test_ontology(self):
        """
        Test the FHIROntologyTable dimension_list function against the Observation, DomainResource and Resource elements
        """
        from i2fhirb2.fhir.fhirontologytable import FHIROntologyTable

        self.tst_output(FHIROntologyTable(shared_graph).dimension_list(FHIR.Observation), "observation")
        self.assertFalse(create_output_files, "New output files generated")

    def test_complete_load(self):
        """
        Load a complete set of tables to test for recursion and other issues
        :return:
        """
        from i2fhirb2.fhir.fhirontologytable import FHIROntologyTable
        FHIROntologyTable(shared_graph).dimension_list()
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
