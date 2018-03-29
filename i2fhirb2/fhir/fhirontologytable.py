
from typing import Optional, List, cast, Dict, NamedTuple, Set

from fhirtordf.rdfsupport.namespaces import FHIR, W5
from rdflib import URIRef, Graph, RDFS

from i2fhirb2.fhir.fhirconceptdimension import FHIRConceptDimension
from i2fhirb2.fhir.fhirmetadatavocabulary import FMVGraphNode, FMVGraphEdge, FMVGraphNodeWithMultiplicity
from i2fhirb2.fhir.fhirmodifierdimension import FHIRModifierDimension
from i2fhirb2.fhir.fhirontology import ModifierOntologyEntry, ConceptOntologyEntry, OntologyRoot
from i2fhirb2.fhir.fhirspecific import concept_path, concept_path_sans_root, concept_code, rightmost_element, \
    skip_fhir_predicates, skip_fhir_types, composite_uri, DEFAULT_BASE_PATH, w5_infrastructure_categories, concept_name
from i2fhirb2.fhir.fhirw5ontology import FHIRW5Ontology
from i2b2model.metadata.i2b2ontology import OntologyEntry


class DimensionSet(NamedTuple):
    """ A collection of defining elements """
    ontology_dimension: List[OntologyEntry]
    concept_dimension: List[FHIRConceptDimension]
    modifier_dimension: List[FHIRModifierDimension]


class FHIROntologyTable:
    """  The set of i2b2 ontology table entries for the supplied subject or all root concepts
    """
    def __init__(self, g: Graph, name_base: str=DEFAULT_BASE_PATH, modifier_base: str = None) -> None:

        self._name_base = name_base if name_base.endswith('\\') else name_base + '\\'
        self._modifier_base = modifier_base if modifier_base else self._name_base[:-1] + 'Mod'
        if not self._modifier_base.endswith('\\'):
            self._modifier_base += '\\'
        self.graph = g
        self.w5_ontology = FHIRW5Ontology(g)
        OntologyEntry.graph = g

    @staticmethod
    def _all_edges(node: FMVGraphNode) -> Set[FMVGraphEdge]:
        """
        Follow the parents, pulling all edges
        :param node: target node
        :return: list of all edges back to root
        """
        rval = set([e for e in node.edges
                    if e.predicate not in skip_fhir_predicates and e.type_node.node not in skip_fhir_types])
        for p in node.parents:
            if p.node not in skip_fhir_types:
                rval.update(FHIROntologyTable._all_edges(p))
        return rval

    def _modifier_ontology_list(self, parent_path: str, parent_uri: URIRef, modifier_base_path: str, node: FMVGraphNode,
                                modifier_dims: Dict[str, FHIRModifierDimension], in_multiple_elements: bool,
                                inside: Set[URIRef] = None, depth: int=1) \
            -> List[ModifierOntologyEntry]:
        """
        Return a list of modifier ontology entries for the supplied base and graph node
        :param parent_path: Path of parent node
        :param parent_uri: URI of base code
        :param modifier_base_path: Root of modifier path
        :param node: Graph node for URI
        :param in_multiple_elements:
        :param inside: Modifier types already being visited (to prevent recursion)
        :param depth: modifier depth
        :return:
        """
        if inside is None:
            inside = set()
        ontology_modifiers: List[ModifierOntologyEntry] = []
        for edge in self._all_edges(node):
            if edge.type_node.is_primitive or in_multiple_elements:
                modifier_path = self._modifier_base + modifier_base_path + rightmost_element(edge.predicate)[1:]
                ontology_modifiers.append(
                    ModifierOntologyEntry(depth,                # depth
                                          parent_uri,       # subject - uri of concept being modified
                                          edge.predicate,   # URI of the modifier itself
                                          modifier_path,    # path that the modifier is applied to
                                          parent_path,      # modifier path
                                          edge.type_node.is_primitive,  # is leaf
                                          edge.predicate,   #
                                          edge.type_node.node))  # actual type of modifier
                if edge.type_node.is_primitive:
                    modifier_entry = FHIRModifierDimension(edge.predicate,  self._name_base)
                    if modifier_entry.modifier_path not in modifier_dims:
                        modifier_dims[modifier_entry.modifier_path] = modifier_entry
                elif in_multiple_elements:
                    if edge.type_node not in inside:
                        inside.add(edge.type_node)
                        ontology_modifiers += \
                            self._modifier_ontology_list(parent_path,
                                                         parent_uri,
                                                         modifier_base_path + rightmost_element(edge.predicate)[1:],
                                                         edge.type_node,
                                                         modifier_dims,
                                                         True,
                                                         inside,
                                                         depth + 1)
                        inside.remove(edge.type_node)

        return ontology_modifiers

    def dimension_list(self, resource: Optional[URIRef]=None) -> DimensionSet:
        """
        Return the set of ontology entries for all w5 concepts and resources (or resource if it is supplied)
        :param resource: Optional resource URI -- for debugging purposes only.  None means all resources
        :return: List of i2b2 ontology entries
        """
        ontology_entries: List[OntologyEntry] = [cast(OntologyEntry, OntologyRoot(self._name_base))]    # FHIR root node
        concept_dimension_entries: Dict[str, FHIRConceptDimension] = {}
        modifier_dimension_entries: Dict[str, FHIRModifierDimension] = {}

        # Create an entry for all of the W5 paths
        for w5_node in self.w5_ontology.w5_paths():
            ontological_path = self._name_base + concept_path(w5_node.node)
            ontology_entries.append(
                ConceptOntologyEntry(w5_node.node,                  # subject URI
                                     w5_node.path,                  # navigational path
                                     ontological_path,              # Ontological path
                                     is_leaf=False,
                                     is_draggable=True))

            if w5_node.fhir_resource_uri and (resource is None or w5_node.fhir_resource_uri == resource):
                for conc_uri, conc_node_ent in self.fhir_concepts(w5_node.fhir_resource_uri).items():
                    conc_node = conc_node_ent.graph_node
                    if '.' in concept_code(conc_uri):
                        navigational_path = w5_node.path + concept_path_sans_root(conc_uri)
                        ontological_path = self._name_base + concept_path(conc_uri)
                        ontology_entries.append(
                            ConceptOntologyEntry(conc_uri,
                                                 navigational_path,
                                                 ontological_path,
                                                 is_leaf=conc_node.is_primitive,
                                                 is_draggable=True,
                                                 primitive_type=conc_node.node if conc_node.is_primitive else None))

                        concept_dimension_entries[ontological_path] = \
                            FHIRConceptDimension(conc_uri, concept_name(self.graph, conc_uri), self._name_base)
                        ontology_entries += self._modifier_ontology_list(navigational_path,
                                                                         conc_uri,
                                                                         concept_path(conc_uri),
                                                                         conc_node,
                                                                         modifier_dimension_entries,
                                                                         conc_node_ent.is_multiple)

        return DimensionSet(ontology_entries,
                            list(concept_dimension_entries.values()),
                            list(modifier_dimension_entries.values()))

    def _fhir_concept_expansion(self, concept_cd: URIRef, type_node: FMVGraphNode,
                                target: Dict[URIRef, FMVGraphNodeWithMultiplicity], nested: bool = False) -> None:
        """
        Expand all of the descendants of concept_cd until a leaf or a multiple_entries node is encountered
        :param concept_cd: Base resource predicate
        """
        target[concept_cd] = FMVGraphNodeWithMultiplicity(type_node, False)
        for edge in type_node.edges:
            extendedconcept_cd = composite_uri(concept_cd, edge.predicate)
            if not edge.type_node.is_primitive:
                target[extendedconcept_cd] = FMVGraphNodeWithMultiplicity(edge.type_node, edge.multiple_entries)
                if not edge.multiple_entries:
                    self._fhir_concept_expansion(extendedconcept_cd, edge.type_node, target, nested=True)
            elif not nested:
                target[extendedconcept_cd] = FMVGraphNodeWithMultiplicity(edge.type_node, edge.multiple_entries)

    def fhir_concepts(self, resource: Optional[URIRef]=None) -> Dict[URIRef, FMVGraphNodeWithMultiplicity]:
        """
        Return a list of resources in the FMV and the corresponding graph nodes.
        :param resource: Subject to restrict output to for debugging
        :return: A map from the concept URI to the corresponding Graph node
        """
        resources = [resource] if resource else self.fhir_resource_concepts()
        rval = {}           # type: Dict[URIRef, FMVGraphNodeWithMultiplicity]
        for r in resources:
            self._fhir_concept_expansion(r, FMVGraphNode(self.graph, r), rval)
        return rval

    def fhir_resource_concepts(self) -> Set[URIRef]:
        """
        Return the uris for the set of all qualifying FHIR resources
        :return: URIs of all FHIR resources
        """
        return {subj for subj in self.graph.transitive_subjects(RDFS.subClassOf, FHIR.Resource)
                if isinstance(subj, URIRef) and not self.w5_ontology.is_w5_infrastructure(subj)}

    def is_w5_infrastructure(self, subj: URIRef) -> bool:
        """
        Determine whether subj belongs to a w5 infrastructure category
        :param subj: FHIR Element
        :return: True if this is an infrastructure category, false otherwise
        """
        return subj in w5_infrastructure_categories or \
            bool(set(self.graph.transitive_objects(subj, RDFS.subClassOf)).intersection(w5_infrastructure_categories))
