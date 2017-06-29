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


class TableNamesTestCase(unittest.TestCase):
    def test(self):
        from i2fhirb2.i2b2model.tablenames import i2b2table
        self.assertEqual("concept_dimension", i2b2table.concept_dimension)
        self.assertEqual("ontology_table", i2b2table.ontology_table)
        self.assertEqual("custom_meta", i2b2table.phys_name(i2b2table.ontology_table))
        self.assertEqual("concept_dimension", i2b2table.phys_name(i2b2table.concept_dimension))
        with self.assertRaises(AttributeError):
            _ = i2b2table.other_dimension
        with self.assertRaises(KeyError):
            _ = i2b2table.phys_name("foo")
        self.assertEqual([
             'concept_dimension',
             'modifier_dimension',
             'ontology_table',
             'patient_dimension',
             'provider_dimension',
             'table_access',
             'visit_dimension'], i2b2table.all_tables())
        from pprint import PrettyPrinter; pp = PrettyPrinter().pprint
        pp(i2b2table.all_tables())

if __name__ == '__main__':
    unittest.main()
