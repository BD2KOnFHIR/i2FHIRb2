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
from collections import OrderedDict


class TableAccessTestCase(unittest.TestCase):
    def test(self):
        from i2fhirb2.i2b2model.i2b2tableaccess import TableAccess
        ta = TableAccess()
        self.assertEqual(('c_table_cd\tc_table_name\tc_protected_access\tc_hlevel\tc_fullname\tc_name\t'
                          'c_synonym_cd\tc_visualattributes\tc_totalnum\tc_basecode\tc_metadataxml\t'
                          'c_facttablecolumn\tc_dimtablename\tc_columnname\tc_columndatatype\tc_operator\t'
                          'c_dimcode\tc_comment\tc_tooltip\tc_entry_date\tc_change_date\tc_status_cd\t'
                          'valuetype_cd'), ta._header())
        self.assertEqual(OrderedDict([
             ('c_table_cd', 'FHIR'),
             ('c_table_name', 'custom_meta'),
             ('c_protected_access', 'N'),
             ('c_hlevel', 1),
             ('c_fullname', '\\FHIR\\'),
             ('c_name', 'FHIR Resources'),
             ('c_synonym_cd', 'N'),
             ('c_visualattributes', 'CA '),
             ('c_totalnum', None),
             ('c_basecode', None),
             ('c_metadataxml', None),
             ('c_facttablecolumn', 'concept_cd'),
             ('c_dimtablename', 'concept_dimension'),
             ('c_columnname', 'concept_path'),
             ('c_columndatatype', 'T'),
             ('c_operator', 'like'),
             ('c_dimcode', '\\FHIR\\'),
             ('c_comment', None),
             ('c_tooltip', 'FHIR Resource'),
             ('c_entry_date', None),
             ('c_change_date', None),
             ('c_status_cd', None),
             ('valuetype_cd', None)]), ta._freeze())


if __name__ == '__main__':
    unittest.main()
