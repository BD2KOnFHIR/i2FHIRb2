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

from i2fhirb2.fhir.fhirspecific import concept_path, concept_code, modifier_code, modifier_name, \
    concept_name
from i2fhirb2.i2b2model.metadata.dimensionmetadata import metadata_xml
from i2fhirb2.i2b2model.metadata.i2b2ontologyquery import Query, ModifierQuery, ConceptQuery, EmptyQuery
from i2fhirb2.i2b2model.metadata.i2b2ontologyvisualattributes import VisualAttributes
from i2fhirb2.i2b2model.shared.i2b2core import I2B2Core
from i2fhirb2.sqlsupport.dynobject import DynElements, DynObject


class OntologyEntry(I2B2Core):
    _t = DynElements(I2B2Core)
    graph = None                # type: Graph
    ontology_name = "FHIR"

    def __init__(self,
                 c_full_name: str,
                 query: Query,
                 visualattributes: VisualAttributes = None,
                 c_basecode: Optional[str]=None,
                 primitive_type: Optional[URIRef]=None,
                 **kwargs):
        """
        Initialize an ontology entry.
        :param c_full_name: Full name of entry (e.g. '\\FHIR\\class\\subclass\\...\\item\\')
        :param query: Dimension table query for item
        :param visualattributes: VisualAttributes for item
        :param c_basecode: "uri" for item
        :param primitive_type: type used to construct c_metadataxml
        :param kwargs: Additional arguments for i2b2_core
        """
        super().__init__(**kwargs)
        assert(c_full_name.endswith('\\'))
        self._c_fullname = c_full_name
        self._query = query
        self._visualattributes = visualattributes if visualattributes else VisualAttributes()
        self._c_basecode = c_basecode
        self._modifier_exclusion = False
        self._primitive_type = primitive_type

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
        return metadata_xml(self._primitive_type, self.c_basecode, self.c_name, self.update_date) \
            if self._primitive_type else None

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
        return 'X' if self._modifier_exclusion else None

    @DynObject.entry(_t)
    def c_path(self) -> Optional[str]:
        # return self.basename[:-1].rsplit('\\', 1)[0]
        return None

    @DynObject.entry(_t)
    def c_symbol(self) -> Optional[str]:
        # return self.basename[:-1].rsplit('\\', 1)[1]
        return None

    def __lt__(self, other):
        return self.c_fullname + self.m_applied_path < other.c_fullname + self.m_applied_path

    def __eq__(self, other):
        return self.c_fullname + self.m_applied_path == other.c_fullname + self.m_applied_path


class OntologyRoot(OntologyEntry):
    _t = DynElements(OntologyEntry)

    def __init__(self, base: str, **kwargs) -> None:
        """
        Initialize an ontology header.
        :param kwargs: Additional arguments for i2b2_core
        """
        if base.startswith('\\'):
            base = base[1:-1]
        path = '\\' + base + '\\'
        super().__init__(path, EmptyQuery(), VisualAttributes("CA"), sourcesystem_cd=base, **kwargs)
        self._base = base

    @DynObject.entry(_t)
    def c_hlevel(self) -> int:
        return 0

    @DynObject.entry(_t)
    def c_name(self) -> str:
        return self._base

    @DynObject.entry(_t)
    def c_basecode(self) -> Optional[str]:
        return self._base + ':'


class ModifierOntologyEntry(OntologyEntry):
    _t = DynElements(OntologyEntry)

    def __init__(self,
                 depth: int,
                 subject: URIRef,
                 mod: URIRef,
                 full_path: str,
                 applied_path: str,
                 is_leaf: bool,
                 mod_pred: URIRef,
                 mod_type: URIRef) -> None:
        """
        Construct a concept entry in the ontology space
        :param depth: Relative one-based depth of entry
        :param subject: URI of concept being modified
        :param mod: URI of modifier itself
        :param full_path: modifier path
        :param applied_path: path that modifier applies to
        :param is_leaf: true if there are no additional children
        :param mod_pred: real modifier predicate (for dimcode)
        :param mod_type: Actual type of path
        """
        assert(depth > 0)

        # TODO: Fix the hard coded reference below
        query = ModifierQuery('\\FHIR\\' + concept_path(mod_pred)) if is_leaf else EmptyQuery()

        visattr = VisualAttributes()
        visattr.leaf = is_leaf
        visattr.concept = False
        visattr.draggable = True
        visattr.editable = False

        super().__init__(full_path, query, visattr, modifier_code(mod), mod_type)

        self._subject = subject
        self._mod = mod
        self._depth = depth
        self._m_applied_path = applied_path
        self._mod_pred = mod_pred

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
        if not rval and self._primitive_type:
            rval = self.graph.comment(self._primitive_type)
        return str(rval) if rval else None

    @DynObject.entry(_t)
    def c_tooltip(self) -> Optional[str]:
        rval = self.graph.value(self._mod, DC.title, None, self.graph.comment(self._mod))
        if not rval and self._primitive_type:
            rval = self.graph.value(self._primitive_type, DC.title, None, self.graph.comment(self._primitive_type))
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
                 is_leaf: bool,
                 is_draggable: bool=True,
                 primitive_type: Optional[URIRef]=None):
        """
        Construct a concept entry in the ontology space
        :param subject: URI of concept
        :param navigational_path: path to concept for navigational purposes.
          Example: \\FHIR\\administrative\\individual\\Patient
        :param ontological_path: concept_dimension path to concept.  Example: \\FHIR\\Patient
        :param is_leaf: true if there are no additional children.
        :param is_draggable: If not a leaf, whether this is an i2b2 container (False) or folder (True)
        :param primitive_type: Type used to construct c_metadataxml
        """
        self._subject = subject

        visattr = VisualAttributes()
        visattr.leaf = is_leaf
        visattr.concept = True
        visattr.draggable = is_draggable
        visattr.editable = False

        full_path = navigational_path
        self._m_applied_path = '@'

        query = ConceptQuery(ontological_path) if is_draggable else EmptyQuery()
        super().__init__(full_path, query, visattr, concept_code(subject), primitive_type)

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
