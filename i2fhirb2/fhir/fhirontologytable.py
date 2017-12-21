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

from typing import Optional, List, cast, Dict, NamedTuple, Set

from rdflib import URIRef, Graph

from i2fhirb2.fhir.fhirmetadata import FHIRMetadata
from i2fhirb2.fhir.fhirmetadatavocabulary import FMVGraphNode, FMVGraphEdge
from i2fhirb2.fhir.fhirspecific import concept_path, concept_path_sans_root, concept_code, rightmost_element, \
    skip_fhir_predicates, skip_fhir_types
from i2fhirb2.i2b2model.metadata.i2b2conceptdimension import ConceptDimension
from i2fhirb2.i2b2model.metadata.i2b2modifierdimension import ModifierDimension
from i2fhirb2.i2b2model.metadata.i2b2ontology import OntologyEntry, OntologyRoot, ConceptOntologyEntry, \
    ModifierOntologyEntry


class DimensionSet(NamedTuple):
    ontology_dimension: List[OntologyEntry]
    concept_dimension: List[ConceptDimension]
    modifier_dimension: List[ModifierDimension]


class FHIROntologyTable(FHIRMetadata):
    """  The set of i2b2 ontology table entries for the supplied subject or all root concepts
    """
    def __init__(self, g: Graph, name_base: str=None, modifier_base: str = None) -> None:
        super().__init__(g, name_base=name_base, modifier_base=modifier_base)
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
                                modifier_dims: Dict[str, ModifierDimension], in_multiple_elements: bool,
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
                    modifier_entry = ModifierDimension(edge.predicate, self._name_base)
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
        # TODO: Figure out how to get DomainResource and Resource concepts into this
        # TODO: DomainResource entries
        # TODO: Where is Observation.component???
        ontology_entries: List[OntologyEntry] = [cast(OntologyEntry, OntologyRoot(self._name_base))]    # FHIR root node
        concept_dimension_entries: Dict[str, ConceptDimension] = {}
        modifier_dimension_entries: Dict[str, ModifierDimension] = {}

        # Create an entry for all of the W5 paths
        for w5_node in self._fhir_metadatavocabulary.w5_graph.w5_paths():
            ontological_path = self._name_base + concept_path(w5_node.node)
            ontology_entries.append(
                ConceptOntologyEntry(w5_node.node,                  # subject URI
                                     w5_node.path,                  # navigational path
                                     ontological_path,              # Ontological path
                                     is_leaf=False,
                                     is_draggable=False))

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

                        concept_dimension_entries[ontological_path] = ConceptDimension(conc_uri, self._name_base)
                        ontology_entries += self._modifier_ontology_list(navigational_path,
                                                                         conc_uri,
                                                                         concept_path(conc_uri),
                                                                         conc_node,
                                                                         modifier_dimension_entries,
                                                                         conc_node_ent.is_multiple)

        return DimensionSet(ontology_entries,
                            list(concept_dimension_entries.values()),
                            list(modifier_dimension_entries.values()))
