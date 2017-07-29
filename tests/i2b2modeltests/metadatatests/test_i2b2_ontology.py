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

import datetime
import unittest
from collections import OrderedDict

from tests.utils.shared_graph import shared_graph


class OntologyTestCase(unittest.TestCase):
    def test_basics(self):
        from i2fhirb2.i2b2model.metadata.i2b2ontology import OntologyEntry
        from i2fhirb2.i2b2model.metadata.i2b2ontologyquery import ConceptQuery

        OntologyEntry.download_date = datetime.datetime(2017, 5, 25)
        OntologyEntry.sourcesystem_cd = "FHIR"
        OntologyEntry.import_date = datetime.datetime(2017, 5, 25)
        OntologyEntry.update_date = datetime.datetime(2001, 12, 1)
        ontrec = OntologyEntry('\\X\\Y\\Z\\', ConceptQuery('\\X\\Y\\Z\\'), None, "17400008")
        self.assertEqual('c_hlevel\tc_fullname\tc_name\tc_synonym_cd\tc_visualattributes\t'
                         'c_totalnum\tc_basecode\tc_metadataxml\tc_facttablecolumn\tc_tablename\t'
                         'c_columnname\tc_columndatatype\tc_operator\tc_dimcode\tc_comment\t'
                         'c_tooltip\tm_applied_path\tupdate_date\tdownload_date\t'
                         'import_date\tsourcesystem_cd\tvaluetype_cd\tm_exclusion_cd\tc_path\tc_symbol',
                         ontrec._header())
        # Note that hierarchy level is zero based
        self.assertEqual(OrderedDict([
             ('c_hlevel', 2),
             ('c_fullname', '\\X\\Y\\Z\\'),
             ('c_name', 'Z'),
             ('c_synonym_cd', 'N'),
             ('c_visualattributes', 'FAE'),
             ('c_totalnum', None),
             ('c_basecode', '17400008'),
             ('c_metadataxml', None),
             ('c_facttablecolumn', 'concept_cd'),
             ('c_tablename', 'concept_dimension'),
             ('c_columnname', 'concept_path'),
             ('c_columndatatype', 'T'),
             ('c_operator', 'like'),
             ('c_dimcode', '\\X\\Y\\Z\\'),
             ('c_comment', None),
             ('c_tooltip', None),
             ('m_applied_path', '@'),
             ('update_date', datetime.datetime(2001, 12, 1, 0, 0)),
             ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('valuetype_cd', None),
             ('m_exclusion_cd', None),
             ('c_path', None),
             ('c_symbol', None)]), ontrec._freeze())

    def test_ontology_entry(self):
        from i2fhirb2.fhir.fhirspecific import FHIR
        from i2fhirb2.i2b2model.metadata.i2b2ontology import ConceptOntologyEntry, OntologyEntry, ModifierOntologyEntry

        OntologyEntry._clear()
        navigational_path = '\\FHIR\\administrative\\individual\\'
        ontology_path = "\\FHIR\\"
        OntologyEntry.graph = shared_graph
        OntologyEntry.sourcesystem_cd = "STU3"
        OntologyEntry.update_date = datetime.datetime(2017, 5, 25, 13, 0)
        subj = FHIR.Patient
        o = ConceptOntologyEntry(subj,
                                 navigational_path,
                                 ontology_path,
                                 False)
        self.assertEqual(OrderedDict([
             ('c_hlevel', 3),
             ('c_fullname', '\\FHIR\\administrative\\individual\\Patient\\'),
             ('c_name', 'Patient'),
             ('c_synonym_cd', 'N'),
             ('c_visualattributes', 'FA '),
             ('c_totalnum', None),
             ('c_basecode', 'FHIR:Patient'),
             ('c_metadataxml', None),
             ('c_facttablecolumn', 'concept_cd'),
             ('c_tablename', 'concept_dimension'),
             ('c_columnname', 'concept_path'),
             ('c_columndatatype', 'T'),
             ('c_operator', 'like'),
             ('c_dimcode', '\\FHIR\\Patient\\'),
             ('c_comment',
              'Demographics and other administrative information about an '
              'individual or animal receiving care or other health-related '
              'services.'),
             ('c_tooltip',
              'Demographics and other administrative information about an '
              'individual or animal receiving care or other health-related '
              'services.'
              ),
             ('m_applied_path', '@'),
             ('update_date', datetime.datetime(2017, 5, 25, 13, 0)),
             ('download_date', datetime.datetime(2017, 5, 25, 13, 0)),
             ('import_date', datetime.datetime(2017, 5, 25, 13, 0)),
             ('sourcesystem_cd', 'STU3'),
             ('valuetype_cd', None),
             ('m_exclusion_cd', None),
             ('c_path', None),
             ('c_symbol', None)]), o._freeze())
        
        subj = FHIR.Patient
        mod = FHIR.Patient.active
        o = ModifierOntologyEntry(1,
                                  subj,
                                  mod,
                                  navigational_path + 'Patient\\',
                                  ontology_path,
                                  True,
                                  mod,
                                  FHIR.boolean)

        self.assertEqual(OrderedDict([
             ('c_hlevel', 1),
             ('c_fullname',  '\\Patient\\active\\'),
             ('c_name', 'active'),
             ('c_synonym_cd', 'N'),
             ('c_visualattributes', 'RA '),
             ('c_totalnum', None),
             ('c_basecode', 'FHIR:Patient.active'),
             ('c_metadataxml',
              '<?xml version="1.0"?>\n'
              '<ValueMetadata>\n'
              '    <Version>3.02</Version>\n'
              '    <CreationDateTime>2017-05-25 13:00:00</CreationDateTime>\n'
              '    <TestID>FHIR:Patient.active</TestID>\n'
              '    <TestName>active</TestName>\n'
              '    <DataType>Enum</DataType>\n'
              '    <Flagstouse/>\n'
              '    <Oktousevalues>Y</Oktousevalues>\n'
              '    <EnumValues>\n'
              '        <Val description="True value">True</Val>\n'
              '        <Val description="False value">False</Val>\n'
              '    </EnumValues>\n'
              '    <UnitValues/>\n'
              '</ValueMetadata>'),
             ('c_facttablecolumn', 'modifier_cd'),
             ('c_tablename', 'modifier_dimension'),
             ('c_columnname', 'modifier_path'),
             ('c_columndatatype', 'T'),
             ('c_operator', 'like'),
             ('c_dimcode', '\\FHIR\\Patient\\active\\'),
             ('c_comment', 'Whether this patient record is in active use.'),
             ('c_tooltip', "Whether this patient's record is in active use"),
             ('m_applied_path', '\\FHIR\\administrative\\individual\\Patient\\'),
             ('update_date', datetime.datetime(2017, 5, 25, 13, 0)),
             ('download_date', datetime.datetime(2017, 5, 25, 13, 0)),
             ('import_date', datetime.datetime(2017, 5, 25, 13, 0)),
             ('sourcesystem_cd', 'STU3'),
             ('valuetype_cd', None),
             ('m_exclusion_cd', None),
             ('c_path', None),
             ('c_symbol', None)]), o._freeze())

    def test_ontology_root(self):
        from i2fhirb2.i2b2model.metadata.i2b2ontology import OntologyRoot, OntologyEntry
        OntologyRoot._clear()
        OntologyEntry._clear()
        o = OntologyRoot("FHIR")
        OntologyRoot.update_date = datetime.datetime(2017, 5, 25, 13, 0)
        self.assertEqual(('0\t\\FHIR\\\tFHIR\tN\tCA \t\tFHIR:\t\tconcept_cd\tconcept_dimension\t'
                          'concept_path\tT\tlike\t\\FHIR\\\t\t\t@\t2017-05-25 13:00:00\t2017-05-25 '
                          '13:00:00\t2017-05-25 13:00:00\tFHIR\t\t\t\t'), repr(o))

if __name__ == '__main__':
    unittest.main()
