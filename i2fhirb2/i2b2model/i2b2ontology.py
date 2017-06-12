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

from rdflib import URIRef, Graph
from rdflib.namespace import DC

from i2fhirb2.fhir.fhirspecific import concept_path, concept_code, modifier_path, modifier_code, modifier_name, \
    concept_name
from i2fhirb2.i2b2model.dimension_query import Query, ModifierQuery, ConceptQuery
from i2fhirb2.i2b2model.i2b2core import I2B2_Core
from i2fhirb2.i2b2model.metadata_xml import metadata_xml
from i2fhirb2.i2b2model.visual_attributes import VisualAttributes
from i2fhirb2.sqlsupport.dynobject import DynElements, DynObject


class OntologyEntry(I2B2_Core):
    _t = DynElements(I2B2_Core)
    graph = None                # type: Graph
    ontology_name = "FHIR"

    def __init__(self,
                 c_full_name: str,
                 query: Query,
                 visualattributes: VisualAttributes = None,
                 c_basecode: Optional[str]=None,
                 **kwargs):
        """
        Initialize an ontology entry.
        :param c_full_name: Full name of entry (e.g. '\\FHIR\\class\\subclass\\...\\item\\')
        :param query: Dimension table query for item
        :param visualattributes: VisualAttributes for item
        :param c_basecode: "uri" for item
        :param kwargs: Additional arguments for i2b2_core
        """
        super().__init__(**kwargs)
        assert(c_full_name.endswith('\\'))
        self._c_fullname = c_full_name
        self._query = query
        self._visualattributes = visualattributes if visualattributes else VisualAttributes()
        self._c_basecode = c_basecode
        self._modifier_exclusion = False

    @DynObject.entry(_t)
    def c_hlevel(self) -> int:
        return self.c_fullname[:-1].count('\\') - 1

    @DynObject.entry(_t)
    def c_fullname(self) -> str:
        return self._c_fullname

    @DynObject.entry(_t)
    def c_name(self) -> str:
        return self.c_fullname[:-1].rsplit('\\', 1)[1]

    @DynObject.entry(_t)
    def c_synonym_cd(self) -> str:
        """ Two or more synonyms of each other will have the same c_basecode """
        return "N"

    @DynObject.entry(_t)
    def c_visualattributes(self) -> str:
        return str(self._visualattributes)

    @DynObject.entry(_t)
    def c_totalnum(self) -> Optional[int]:
        return None

    @DynObject.entry(_t)
    def c_basecode(self) -> Optional[str]:
        return self._c_basecode

    @DynObject.entry(_t)
    def c_metadataxml(self) -> Optional[str]:
        return None

    @DynObject.entry(_t)
    def c_facttablecolumn(self) -> str:
        return self._query.key

    @DynObject.entry(_t)
    def c_tablename(self) -> str:
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
        return None

    @DynObject.entry(_t)
    def m_applied_path(self) -> str:
        return '@' if not isinstance(self._query, ModifierQuery) else self.c_fullname[:-1].rsplit('\\', 1)[0] + '\\%'

    DynObject._after_root(_t)

    @DynObject.entry(_t)
    def valuetype_cd(self) -> Optional[str]:
        return None

    @DynObject.entry(_t)
    def m_exclusion_cd(self) -> Optional[str]:
        return 'X' if self._modifier_exclusion else None

    @DynObject.entry(_t)
    def c_path(self) -> Optional[str]:
        # return self.basename[:-1].rsplit('\\', 1)[0]
        return None

    @DynObject.entry(_t)
    def c_symbol(self) -> Optional[str]:
        # return self.basename[:-1].rsplit('\\', 1)[1]
        return None


class OntologyRoot(I2B2_Core):
    _t = DynElements(I2B2_Core)

    def __init__(self, base: str, **kwargs):
        """
        Initialize an ontology header.
        :param kwargs: Additional arguments for i2b2_core
        """
        super().__init__(sourcesystem_cd=base, **kwargs)
        self._base = base
        self._fullname = '\\' + base + '\\'
        self._visualattributes = VisualAttributes("CA")
        self._query = ConceptQuery(self._fullname)

    @DynObject.entry(_t)
    def c_hlevel(self) -> int:
        return 0

    @DynObject.entry(_t)
    def c_fullname(self) -> str:
        return "\\" + self._base + "\\"

    @DynObject.entry(_t)
    def c_name(self) -> str:
        return self._base

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
        return self._base

    @DynObject.entry(_t)
    def c_metadataxml(self) -> Optional[str]:
        return None

    @DynObject.entry(_t)
    def c_facttablecolumn(self) -> str:
        return self._query.key

    @DynObject.entry(_t)
    def c_tablename(self) -> str:
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
        return None

    @DynObject.entry(_t)
    def m_applied_path(self) -> str:
        return '@'

    DynObject._after_root(_t)

    @DynObject.entry(_t)
    def valuetype_cd(self) -> Optional[str]:
        return None

    @DynObject.entry(_t)
    def m_exclusion_cd(self) -> Optional[str]:
        return None

    @DynObject.entry(_t)
    def c_path(self) -> Optional[str]:
        return None

    @DynObject.entry(_t)
    def c_symbol(self) -> Optional[str]:
        # return self.basename[:-1].rsplit('\\', 1)[1]
        return None

    def __lt__(self, other):
        return self.c_fullname + self.m_applied_path < other.c_fullname + self.m_applied_path

    def __eq__(self, other):
        return self.c_fullname + self.m_applied_path == other.c_fullname + self.m_applied_path


class ModifierOntologyEntry(OntologyEntry):
    _t = DynElements(OntologyEntry)

    def __init__(self,
                 depth: int,
                 subject: URIRef,
                 mod: URIRef,
                 full_concept_path: str,
                 modifier_base_path: str,
                 is_leaf: bool,
                 primitive_type: Optional[URIRef] = None):
        """
        Construct a concept entry in the ontology space
        :param depth: Relative one-based depth of entry
        :param subject: URI of concept being modified
        :param mod: URI of modifier itself
        :param full_concept_path: concept path to which this modifier applies.  Unchanged.
        :param modifier_base_path: base path for the modifier dimension query.
        :param is_leaf: true if there are no additional children
        :param primitive_type: true means generate metadata xml entry
        """
        assert(depth > 0)

        full_path = '\\' + concept_path(subject) + (modifier_path(mod) if subject != mod else '')
        query = ModifierQuery(modifier_base_path + full_path[1:])

        visattr = VisualAttributes()
        visattr.leaf = is_leaf
        visattr.concept = False
        visattr.draggable = True
        visattr.editable = False

        super().__init__(full_path, query, visattr, modifier_code(mod))

        self._subject = subject
        self._mod = mod
        self._depth = depth
        self._primitive_type = primitive_type
        self._m_applied_path = full_concept_path

    # Levels in ontology modifier references start at 1
    @DynObject.entry(_t)
    def c_hlevel(self) -> int:
        return self._depth

    @DynObject.entry(_t)
    def c_name(self) -> str:
        return modifier_name(self.graph, self._mod)

    @DynObject.entry(_t)
    def c_comment(self) -> Optional[str]:
        rval = self.graph.comment(self._mod)
        return str(rval) if rval else None

    @DynObject.entry(_t)
    def c_metadataxml(self) -> Optional[str]:
        return metadata_xml(self._primitive_type, self.c_basecode, self.c_name) if self._primitive_type else None

    @DynObject.entry(_t)
    def c_tooltip(self) -> Optional[str]:
        rval = self.graph.value(self._mod, DC.title, None, self.graph.comment(self._mod))
        return str(rval) if rval else None

    @DynObject.entry(_t)
    def m_applied_path(self) -> str:
        return self._m_applied_path


class ConceptOntologyEntry(OntologyEntry):
    _t = DynElements(OntologyEntry)

    def __init__(self,
                 subject: URIRef,
                 navigational_path: str,
                 ontological_path: str,
                 is_leaf: bool):
        """
        Construct a concept entry in the ontology space
        :param subject: URI of concept
        :param navigational_path: path to concept for navigational purposes.
          Example: \\FHIR\\administrative\\individual\\Patient
        :param ontological_path: concept_dimension path to concept.  Example: \\FHIR\\Patient
        :param is_leaf: true if there are no additional children.
        """
        self._subject = subject

        visattr = VisualAttributes()
        visattr.leaf = is_leaf
        visattr.concept = True
        visattr.draggable = True
        visattr.editable = False

        full_path = navigational_path + concept_path(subject)

        query = ConceptQuery(ontological_path + concept_path(subject))
        super().__init__(full_path, query, visattr, concept_code(subject))

    # Level in ontology concept references are relative to base path
    @DynObject.entry(_t)
    def c_hlevel(self) -> int:
        return self.c_fullname[:-1].count('\\') - 1

    @DynObject.entry(_t)
    def c_name(self) -> str:
        return concept_name(self.graph, self._subject)

    @DynObject.entry(_t)
    def c_comment(self) -> Optional[str]:
        rval = self.graph.comment(self._subject)
        return str(rval) if rval else None

    @DynObject.entry(_t)
    def c_tooltip(self) -> Optional[str]:
        rval = self.graph.value(self._subject, DC.title, None, self.graph.comment(self._subject))
        return str(rval) if rval else None
