from typing import Optional

from i2b2model.metadata.i2b2ontology import OntologyEntry
from i2b2model.metadata.i2b2ontologyquery import ModifierQuery, EmptyQuery, ConceptQuery
from i2b2model.metadata.i2b2ontologyvisualattributes import VisualAttributes
from rdflib import URIRef
from rdflib.namespace import DC

from i2fhirb2.fhir.fhirdimensionmetadata import metadata_xml
from i2fhirb2.fhir.fhirspecific import concept_path, modifier_code, modifier_name, concept_code, concept_name


class ModifierOntologyEntry(OntologyEntry):

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

        super().__init__(full_path, query, visattr, modifier_code(mod))

        self._subject = subject
        self._mod = mod
        self._mod_pred = mod_pred
        self._primitive_type = mod_type

        self.c_hlevel = depth
        self.m_applied_path = applied_path

    def c_name(self) -> str:
        return modifier_name(self.graph, self._mod)

    def c_metadataxml(self) -> Optional[str]:
        # noinspection PyTypeChecker
        return metadata_xml(self._primitive_type, self.c_basecode, self.c_name, self.update_date) \
            if self._primitive_type else None

    def c_comment(self) -> Optional[str]:
        rval = self.graph.comment(self._mod)
        if not rval and self._primitive_type:
            rval = self.graph.comment(self._primitive_type)
        return str(rval) if rval else None

    def c_tooltip(self) -> Optional[str]:
        rval = self.graph.value(self._mod, DC.title, None, self.graph.comment(self._mod))
        if not rval and self._primitive_type:
            rval = self.graph.value(self._primitive_type, DC.title, None, self.graph.comment(self._primitive_type))
        return str(rval) if rval else None


class ConceptOntologyEntry(OntologyEntry):

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
        self._primitive_type = primitive_type

        query = ConceptQuery(ontological_path) if is_draggable else EmptyQuery()
        super().__init__(full_path, query, visattr, concept_code(subject))

        self.m_applied_path = '@'

    def c_name(self) -> str:
        return concept_name(self.graph, self._subject)

    def c_metadataxml(self) -> Optional[str]:
        # noinspection PyTypeChecker
        return metadata_xml(self._primitive_type, self.c_basecode, self.c_name, self.update_date) \
            if self._primitive_type else None

    def c_comment(self) -> Optional[str]:
        rval = self.graph.comment(self._subject)
        return str(rval) if rval else None

    def c_tooltip(self) -> Optional[str]:
        rval = self.graph.value(self._subject, DC.title, None, self.graph.comment(self._subject))
        return str(rval) if rval else None


class OntologyRoot(OntologyEntry):
    def __init__(self, base: str):
        fullname = ('\\' if not base.startswith('\\') else '') + base + ('\\' if not base.endswith('\\') else '')
        super().__init__(fullname, EmptyQuery(), VisualAttributes('CA'))
        self.c_basecode = self.c_name + ':'

