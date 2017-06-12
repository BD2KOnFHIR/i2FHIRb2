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


class DimensionQueryTestCase(unittest.TestCase):

    def test_concept_query(self):
        from i2fhirb2.i2b2model.dimension_query import ConceptQuery
        from i2fhirb2.i2b2model.i2b2ontology import OntologyEntry

        q = ConceptQuery("foo")
        self.assertEqual("SELECT concept_cd\nFROM concept_dimension\nWHERE concept_path like 'foo'", str(q))
        q.where_obj = '\\path\\%'
        self.assertEqual("SELECT concept_cd\nFROM concept_dimension\nWHERE concept_path like '\\path\\%'", str(q))
        o = OntologyEntry("\\PATH\\subpath\\", ConceptQuery('\\PATH\\subpath\\'), None, "74400008")
        self.assertEqual(o.c_facttablecolumn, 'concept_cd')
        self.assertEqual(o.c_tablename, 'concept_dimension')
        self.assertEqual(o.c_columndatatype, 'T')
        self.assertEqual(o.c_columnname, 'concept_path')
        self.assertEqual(o.c_operator, 'like')
        self.assertEqual(o.c_dimcode, '\\PATH\\subpath\\')

    def test_modifier_query(self):
        from i2fhirb2.i2b2model.dimension_query import ModifierQuery
        from i2fhirb2.i2b2model.i2b2ontology import OntologyEntry

        q = ModifierQuery("foo")
        self.assertEqual("SELECT modifier_cd\nFROM modifier_dimension\nWHERE modifier_path like 'foo'", str(q))
        o = OntologyEntry("\\PATH\\subpath\\", ModifierQuery('\\PATH\\subpath\\'), None, "74400008")
        self.assertEqual(o.c_facttablecolumn, 'modifier_cd')
        self.assertEqual(o.c_tablename, 'modifier_dimension')
        self.assertEqual(o.c_columndatatype, 'T')
        self.assertEqual(o.c_columnname, 'modifier_path')
        self.assertEqual(o.c_operator, 'like')
        self.assertEqual(o.c_dimcode, '\\PATH\\subpath\\')

    def test_patient_query(self):
        from i2fhirb2.i2b2model.dimension_query import PatientQuery
        from i2fhirb2.i2b2model.i2b2ontology import OntologyEntry

        q = PatientQuery('patient_num', '=', 12345)
        self.assertEqual("SELECT patient_num\nFROM patient_dimension\nWHERE patient_num = 12345", str(q))
        pq = PatientQuery(
            'birth_date',
            'BETWEEN',
            "(CURRENT_DATE - INTERVAL '731.5 day') AND"
            " (CURRENT_DATE - INTERVAL '366.25 day')")
        self.assertEqual("SELECT patient_num\nFROM patient_dimension\n"
                         "WHERE birth_date BETWEEN "
                         "(CURRENT_DATE - INTERVAL '731.5 day') AND "
                         "(CURRENT_DATE - INTERVAL '366.25 day')", str(pq))
        o = OntologyEntry("\\PATH\\subpath\\", pq, None, "Q117.3")
        self.assertEqual(o.c_facttablecolumn, 'patient_num')
        self.assertEqual(o.c_tablename, 'patient_dimension')
        self.assertEqual(o.c_columndatatype, 'N')
        self.assertEqual(o.c_columnname, 'birth_date')
        self.assertEqual(o.c_operator, 'BETWEEN')
        self.assertEqual(o.c_dimcode, "(CURRENT_DATE - INTERVAL '731.5 day') "
                                      "AND (CURRENT_DATE - INTERVAL '366.25 day')")

    def test_visit_query(self):
        from i2fhirb2.i2b2model.dimension_query import VisitQuery
        from i2fhirb2.i2b2model.i2b2ontology import OntologyEntry

        vq = VisitQuery('length_of_stay', '>', 10)
        self.assertEqual("SELECT encounter_num\nFROM visit_dimension\nWHERE length_of_stay > 10", str(vq))
        o = OntologyEntry("\\PATH\\subpath\\", vq, None, "Q117.3")
        self.assertEqual(o.c_facttablecolumn, 'encounter_num')
        self.assertEqual(o.c_tablename, 'visit_dimension')
        self.assertEqual(o.c_columndatatype, 'N')
        self.assertEqual(o.c_columnname, 'length_of_stay')
        self.assertEqual(o.c_operator, '>')
        self.assertEqual(o.c_dimcode, 10)


if __name__ == '__main__':
    unittest.main()
