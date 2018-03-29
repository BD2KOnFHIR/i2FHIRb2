import os
import unittest
from datetime import datetime
from typing import List, Tuple

from dynprops import row, heading
from i2b2model.shared.i2b2core import I2B2Core

from tests.utils.crc_testcase import CRCTestCase

from i2fhirb2.fhir import fhirdimensionmetadata
from i2fhirb2.fhir.fhirconceptdimension import FHIRConceptDimension
from i2fhirb2.fhir.fhirmodifierdimension import FHIRModifierDimension
from i2fhirb2.fhir.fhirspecific import FHIR
from i2b2model.metadata.i2b2ontology import OntologyEntry
from tests.utils.shared_graph import shared_graph

# True means create the output file -- false means test it
create_output_files = False         # Be very careful when setting this to 'true'


class FHIROntologyTestCase(CRCTestCase):
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

    def setUp(self):
        super().setUp()
        ref_datetime = datetime(2017, 5, 25, 13, 0)
        fhirdimensionmetadata.creation_date = ref_datetime

        from i2fhirb2.fhir.fhirmodifierdimension import FHIRModifierDimension
        I2B2Core.update_date = ref_datetime
        FHIRModifierDimension.graph = shared_graph

        from i2fhirb2.fhir.fhirconceptdimension import FHIRConceptDimension
        FHIRConceptDimension.graph = shared_graph

    @staticmethod
    def esc_output(txt: str) -> str:
        return txt.replace('\r\n', '').replace('\r', '').replace('\n', '').strip('\t')

    def set_sourcesystem_cds(self) -> None:
        I2B2Core.sourcesystem_cd = self._sourcesystem_cd

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
                    outf.write(self.esc_output(row(e)) + '\n')
            self.maxDiff = None
            with open(full_fname, 'r') as outf:
                self.assertEqual(outf.readline().strip(), header, "Header mismatch")
                line_number = 1
                for e in sorted(dimension_entries):
                    line_number += 1
                    self.assertEqual(outf.readline().strip('\r\n\t'), self.esc_output(row(e)),
                                     "Mismatch on line {}".format(line_number))
                self.assertEqual(outf.read(), "")

    def tst_output(self, dimensions: Tuple[List[OntologyEntry], List[FHIRConceptDimension],
                                           List[FHIRModifierDimension]], resource_name: str) -> None:
        """
        Test the output of FHIROntologyTable.dimension_list as generated against resource
        :param dimensions: ontology, concept and modifier dimension entries
        :param resource_name: name of specific test file (e.g. 'observation', 'domain_resource', etc.)
        """
        self.set_sourcesystem_cds()
        self.tst_dimension(heading(OntologyEntry), dimensions[0], 'fhir_ontology_' + resource_name)
        self.tst_dimension(heading(FHIRConceptDimension), dimensions[1], 'fhir_concept_dimension_' + resource_name)
        self.tst_dimension(heading(FHIRModifierDimension), dimensions[2], 'fhir_modifier_dimension_' + resource_name)

    def test_ontology(self):
        """
        Test the FHIROntologyTable dimension_list function against the Observation, DomainResource and Resource elements
        """
        from i2fhirb2.fhir.fhirontologytable import FHIROntologyTable

        with self.sourcesystem_cd():
            self.tst_output(FHIROntologyTable(shared_graph).dimension_list(FHIR.Observation), "observation")
            self.assertFalse(create_output_files, "New output files generated")

    def test_complete_load(self):
        """
        Load a complete set of tables to test for recursion and other issues
        :return:
        """
        from i2fhirb2.fhir.fhirontologytable import FHIROntologyTable

        with self.sourcesystem_cd():
            self.set_sourcesystem_cds()
            FHIROntologyTable(shared_graph).dimension_list()
            self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
