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

from i2fhirb2.fhir.fhirontology import FHIROntology

from i2fhirb2.fhir.fhirspecific import FHIR
from i2fhirb2.i2b2model.i2b2conceptdimension import ConceptDimensionRoot
from i2fhirb2.i2b2model.i2b2ontology import OntologyRoot
from tests.base_test_case import BaseTestCase, shared_graph

# True means create the output file -- false means test it
create_output_files = False


class FHIROntologyTestCase(BaseTestCase):

    @staticmethod
    def esc_output(txt: str) -> str:
        return txt.replace('\r\n', '').replace('\r', '').replace('\n', '')

    def tst_output(self, o: FHIROntology, outfname: str):
        o += shared_graph
        v = o.dimension_list()
        if create_output_files:
            with open(outfname, 'w') as outf:
                outf.write(o.tsv_header() + '\n')
                for e in sorted(v):
                    outf.write(self.esc_output(repr(e)) + '\n')
        self.maxDiff = None
        with open(outfname, 'r') as outf:
            self.assertEqual(outf.readline().strip(), o.tsv_header())
            for e in sorted(v):
                self.assertEqual(outf.readline().strip('\r\n'), self.esc_output(repr(e)))
            self.assertEqual(outf.read(), "")
        self.assertEqual(False, create_output_files, "Test fails if generating the output file")

    def test_concept_dimension(self):
        from i2fhirb2.fhir.fhirontology import FHIRConceptDimension
        from i2fhirb2.i2b2model.i2b2conceptdimension import ConceptDimension
        ConceptDimension._clear()
        ConceptDimension.sourcesystem_cd = "FHIR STU3"
        ConceptDimension.update_date = ConceptDimension.import_date = ConceptDimension.download_date = \
            datetime(2017, 5, 25, 13, 0)
        ConceptDimensionRoot.update_date = datetime(2017, 5, 25, 13, 0)

        self.tst_output(FHIRConceptDimension(),
                        os.path.join(shared_graph.dirname, 'data_out', 'fhir_concept_dimension.tsv'))

    def test_modifier_dimension(self):
        from i2fhirb2.fhir.fhirontology import FHIRModifierDimension
        from i2fhirb2.i2b2model.i2b2modifierdimension import ModifierDimension
        ModifierDimension._clear()
        ModifierDimension.sourcesystem_cd = "FHIR STU3"
        ModifierDimension.update_date = datetime(2017, 5, 25, 13, 0)

        self.tst_output(FHIRModifierDimension(),
                        os.path.join(shared_graph.dirname, 'data_out', 'fhir_modifier_dimension.tsv'))

    def test_ontology(self):
        from i2fhirb2.fhir.fhirontology import FHIROntologyTable
        from i2fhirb2.i2b2model.i2b2ontology import OntologyEntry
        from i2fhirb2.i2b2model import metadata_xml
        metadata_xml.creation_date = datetime(2017, 5, 25, 13, 0)
        OntologyEntry._clear()
        OntologyEntry.sourcesystem_cd = "FHIR STU3"
        OntologyEntry.update_date = datetime(2017, 5, 25, 13, 0)
        OntologyRoot.sourcesystem_cd = "FHIR STU3"
        OntologyRoot.update_date = datetime(2017, 5, 25, 13, 0)

        self.tst_output(FHIROntologyTable(),
                        os.path.join(shared_graph.dirname, 'data_out', 'fhir_ontology.tsv'))

if __name__ == '__main__':
    unittest.main()
