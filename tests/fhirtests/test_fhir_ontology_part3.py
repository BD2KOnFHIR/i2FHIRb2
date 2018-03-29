
import datetime
import unittest
from collections import OrderedDict

from dynprops import as_dict, clear, row
from i2b2model.shared.i2b2core import I2B2Core

from i2fhirb2.fhir.fhirontology import ConceptOntologyEntry, ModifierOntologyEntry, OntologyRoot
from tests.utils.shared_graph import shared_graph


class FHIROntologyP3TestCase(unittest.TestCase):

    def test_concept_ontology_entry(self):
        from i2fhirb2.fhir.fhirspecific import FHIR
        from i2b2model.metadata.i2b2ontology import OntologyEntry

        clear(OntologyEntry)
        navigational_path = '\\FHIR\\administrative\\individual\\Patient\\'
        ontology_path = "\\FHIR\\Patient\\"
        OntologyEntry.graph = shared_graph
        I2B2Core.sourcesystem_cd = "STU3"
        I2B2Core.update_date = datetime.datetime(2017, 5, 25, 13, 0)
        subj = FHIR.Patient
        o = ConceptOntologyEntry(subj,
                                 navigational_path,
                                 ontology_path,
                                 True)
        self.assertEqual(OrderedDict([
             ('c_hlevel', 3),
             ('c_fullname', '\\FHIR\\administrative\\individual\\Patient\\'),
             ('c_name', 'Patient'),
             ('c_synonym_cd', 'N'),
             ('c_visualattributes', 'LA '),
             ('c_totalnum', None),
             ('c_basecode', 'FHIR:Patient'),
             ('c_metadataxml', None),
             ('c_facttablecolumn', 'concept_cd'),
             ('c_tablename', 'concept_dimension'),
             ('c_columnname', 'concept_path'),
             ('c_columndatatype', 'T'),
             ('c_operator', '='),
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
             ('c_symbol', None)]), as_dict(o))

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
            ('c_operator', '='),
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
            ('c_symbol', None)]), as_dict(o))

    def test_modifier_ontology_entry(self):
        from i2fhirb2.fhir.fhirspecific import FHIR
        from i2b2model.metadata.i2b2ontology import OntologyEntry

        clear(OntologyEntry)
        navigational_path = '\\FHIR\\administrative\\individual\\Patient\\'
        modifier_path = "\\FHIRMod\\Patient\\active\\"
        OntologyEntry.graph = shared_graph
        I2B2Core.sourcesystem_cd = "STU3"
        I2B2Core.update_date = datetime.datetime(2017, 5, 25, 13, 0)
        subj = FHIR.Patient
        mod = FHIR.Patient.active
        o = ModifierOntologyEntry(1,
                                  subj,
                                  mod,
                                  modifier_path,
                                  navigational_path,
                                  True,
                                  mod,
                                  FHIR.boolean)

        self.assertEqual(OrderedDict([
             ('c_hlevel', 1),
             ('c_fullname',  '\\FHIRMod\\Patient\\active\\'),
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
             ('c_symbol', None)]), as_dict(o))

    def test_ontology_root(self):
        from i2b2model.metadata.i2b2ontology import OntologyEntry
        clear(OntologyRoot)
        clear(OntologyEntry)
        o = OntologyRoot("FHIR")
        I2B2Core.update_date = datetime.datetime(2017, 5, 25, 13, 0)
        self.assertEqual(('0\t\\FHIR\\\tFHIR\tN\tCA \t\tFHIR:\t\t\t\t'
                          '\tT\t\t\t\t\t@\t2017-05-25 13:00:00\t2017-05-25 '
                          '13:00:00\t2017-05-25 13:00:00\tSTU3\t\t\t\t'), row(o))


if __name__ == '__main__':
    unittest.main()
