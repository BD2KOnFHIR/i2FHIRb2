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
from abc import ABCMeta, abstractmethod
from typing import Optional, List, Dict, Tuple, Set, NamedTuple

from i2fhirb2.fhir.fhirmetadatavocabulary import FHIRMetaDataVocabulary, FMVGraphNode, FMVGraphEdge
from rdflib import Graph, URIRef

from i2fhirb2.fhir.fhirspecific import composite_uri, concept_path, modifier_path
from i2fhirb2.i2b2model.metadata.i2b2ontology import OntologyEntry


class FMVGraphNodeWithMultiplicity(NamedTuple):
    graph_node: "FMVGraphNode"
    is_multiple: bool


class FHIRMetadata(metaclass=ABCMeta):
    """
    The W5 OntologyEntry in i2b2 space
    """

    def __init__(self, g: Graph, name_base: Optional[str]=None, modifier_base: Optional[str]=None) -> None:
        """
        Create a FHIR i2b2 generator
        :param g: Graph containing fhir.ttl information
        :param name_base: Base for concept_dimension / modifier dimension and non-modifier ontology paths
        :param modifier_base: base for modifier ontology paths (m_applied_path != '@')
        """
        if name_base is None:
            name_base = "\\FHIR\\"
        else:
            assert(name_base.endswith('\\'))
        if modifier_base is None:
            modifier_base = name_base[:-1] + "Mod\\"
        self._fhir_metadatavocabulary = FHIRMetaDataVocabulary()
        self._name_base = name_base
        self._modifier_base = modifier_base
        self.graph = g

    def _fhir_concept_expansion(self, concept_cd: URIRef, type_node: FMVGraphNode,
                                target: Dict[URIRef, FMVGraphNodeWithMultiplicity], nested: bool=False) -> None:
        """
        Expand all of the descendants of concept_cd until a leaf or a multiple_entries node is encountered
        :param concept_cd: Base resource predicate
        """
        target[concept_cd] = FMVGraphNodeWithMultiplicity(type_node, False)
        for edge in type_node.edges:
            extended_concept_cd = composite_uri(concept_cd, edge.predicate)
            if not edge.type_node.is_primitive:
                target[extended_concept_cd] = FMVGraphNodeWithMultiplicity(edge.type_node, edge.multiple_entries)
                if not edge.multiple_entries:
                    self._fhir_concept_expansion(extended_concept_cd, edge.type_node, target, nested=True)
            elif not nested:
                target[extended_concept_cd] = FMVGraphNodeWithMultiplicity(edge.type_node, edge.multiple_entries)

    def fhir_concepts(self, resource: Optional[URIRef]=None) -> Dict[URIRef, FMVGraphNodeWithMultiplicity]:
        """
        Return a list of resources in the FMV and the corresponding graph nodes.
        :param resource: Subject to restrict output to for debugging
        :return: A map from the concept URI to the corresponding Graph node
        """
        resources = [resource] if resource else self._fhir_metadatavocabulary.fhir_resource_concepts()
        rval = {}           # type: Dict[URIRef, FMVGraphNodeWithMultiplicity]
        for r in resources:
            self._fhir_concept_expansion(r, self._fhir_metadatavocabulary.resource_graph(r), rval)
        return rval

    def _add_modifier(self, modifier: FMVGraphEdge, target: Dict[URIRef, FMVGraphNode],
                      seen: Set[FMVGraphNode], depth: int=0) -> None:
        if modifier.type_node not in seen:
            if modifier.type_node.is_primitive:
                target[modifier.predicate] = modifier.type_node
            else:
                for edge in modifier.type_node.edges:
                    # seen.add(edge.type_node)
                    self._add_modifier(edge, target, seen, depth+1)

    def dimension_list(self, _: Optional[URIRef]=None) -> List[OntologyEntry]:
        """ Abstract class to return i2b2 dimension entries"""
        return []
