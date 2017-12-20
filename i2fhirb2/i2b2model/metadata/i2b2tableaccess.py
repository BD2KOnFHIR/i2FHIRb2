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
from typing import Optional

from i2fhirb2.i2b2model.metadata.i2b2ontologyquery import ConceptQuery
from i2fhirb2.i2b2model.metadata.i2b2ontologyvisualattributes import VisualAttributes
from i2fhirb2.i2b2model.shared.tablenames import i2b2tablenames
from i2fhirb2.sqlsupport.dynobject import DynObject, DynElements


class TableAccess(DynObject):
    _t = DynElements(DynObject)
    _visualattributes = VisualAttributes("CA")
    _query = ConceptQuery("\\FHIR\\")

    @DynObject.entry(_t)
    def c_table_cd(self) -> str:
        return "FHIR"

    @DynObject.entry(_t)
    def c_table_name(self) -> str:
        return i2b2tablenames.phys_name(i2b2tablenames.ontology_table)

    @DynObject.entry(_t)
    def c_protected_access(self) -> str:
        return "N"

    @DynObject.entry(_t)
    def c_hlevel(self) -> int:
        return 1

    @DynObject.entry(_t)
    def c_fullname(self) -> str:
        return '\\FHIR\\'

    @DynObject.entry(_t)
    def c_name(self) -> str:
        return "FHIR Resources"

    @DynObject.entry(_t)
    def c_synonym_cd(self) -> str:
        return "N"

    @DynObject.entry(_t)
    def c_visualattributes(self) -> str:
        return str(self._visualattributes)

    @DynObject.entry(_t)
    def c_totalnum(self) -> Optional[int]:
        return None

    @DynObject.entry(_t)
    def c_basecode(self) -> Optional[str]:
        return None

    @DynObject.entry(_t)
    def c_metadataxml(self) -> Optional[str]:
        return None

    @DynObject.entry(_t)
    def c_facttablecolumn(self) -> str:
        return self._query.key

    @DynObject.entry(_t)
    def c_dimtablename(self) -> str:
        return self._query.table

    @DynObject.entry(_t)
    def c_columnname(self) -> str:
        return self._query.where_subj

    @DynObject.entry(_t)
    def c_columndatatype(self) -> str:
        return 'N' if self._query.numeric_key else 'T'

    @DynObject.entry(_t)
    def c_operator(self) -> str:
        return self._query.where_pred

    @DynObject.entry(_t)
    def c_dimcode(self) -> str:
        return self._query.where_obj

    @DynObject.entry(_t)
    def c_comment(self) -> Optional[str]:
        return None

    @DynObject.entry(_t)
    def c_tooltip(self) -> Optional[str]:
        return "FHIR Resource"

    @DynObject.entry(_t)
    def c_entry_date(self) -> Optional[str]:
        return None

    @DynObject.entry(_t)
    def c_change_date(self) -> Optional[str]:
        return None

    @DynObject.entry(_t)
    def c_status_cd(self) -> Optional[str]:
        return None

    @DynObject.entry(_t)
    def valuetype_cd(self) -> Optional[str]:
        return None
