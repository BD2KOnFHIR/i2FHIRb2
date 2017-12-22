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
from typing import Set, Dict, List, Union, Tuple

import sys
from fhirtordf.fhir.fhirmetavoc import FHIRMetaVoc
from fhirtordf.rdfsupport.namespaces import FHIR
from rdflib import Graph, URIRef, RDFS, RDF, OWL, BNode
from rdflib.collection import Collection

from i2fhirb2.fhir.fhirspecific import is_primitive, skip_fhir_predicates
from i2fhirb2.fhir.fhirw5ontology import FHIRW5Ontology

# TODO: The FMV needs to be updated to add a type element -- we use this enumeration as a temporary solution
fhir_complex_types = {FHIR.Address, FHIR.Age, FHIR.Annotation, FHIR.Attachment,
                      FHIR.CodeableConcept, FHIR.Coding, FHIR.ContactDetail, FHIR.ContactPoint,
                      FHIR.Count, FHIR.Distance,  FHIR.Duration, FHIR.HumanName,
                      FHIR.Identifier, FHIR.Money, FHIR.Period, FHIR.Quantity, FHIR.Range, FHIR.Ratio,
                      FHIR.Signature, FHIR.SimpleQuantity, FHIR.Timing}

FHIR_str = str(FHIR)


def fns(uri: URIRef) -> str:
    """
    Change URI into fhir:name if appropriate
    :param uri: URI to convert
    :return: ns/name form if FHIR URI else turtle form
    """
    str_uri = str(uri)
    return str_uri.replace(FHIR_str, 'fhir:') if FHIR_str in str_uri else "<{}>".format(str_uri)


def predicate_and_type_for(g: Graph, restriction_node: Union[URIRef, BNode]) -> Tuple[URIRef, URIRef]:
    predicate = g.value(restriction_node, OWL.onProperty)
    predicate_type = g.value(restriction_node, OWL.allValuesFrom)
    if predicate_type is None:
        predicate_type = g.value(restriction_node, OWL.someValuesFrom)
    return predicate, predicate_type


class FMVGraphEdge:
    def __init__(self, g: Graph, restriction_node: Union[URIRef, BNode]) -> None:
        """
        An edge (predicate) in an FMV graph.  Determined by parsing either an existential (OWL:someValuesFrom)
         or universal (OWL:allValuesFrom) element in an OWL:Restriction node.

        Elements:
        * predicate -- URIRef of restriction property (example: FHIR.Observation.status)
        * multiple_entries -- True if element can occur more than one time
        * type_node -- target of edge

        :param g: Graph containing FMV
        :param restriction_node: Restriction entry
        """
        self.predicate, predicate_type = predicate_and_type_for(g, restriction_node)
        self.multiple_entries = int(g.value(restriction_node, OWL.maxCardinality,
                                            default=int(g.value(restriction_node, OWL.cardinality,
                                                                default=sys.maxsize)))) > 1
        if predicate_type not in FMVGraphNode._known_nodes:
            self.type_node = FMVGraphNode(g, predicate_type)
        else:
            self.type_node = FMVGraphNode._known_nodes[predicate_type]

    def as_indented_str(self, indent: int) -> str:
        rval = 4 * indent * ' '
        if indent > 10:
            return rval + '   ...'
        else:
            return rval + fns(self.predicate) + " " + \
                self.type_node.as_indented_str(indent, self.multiple_entries)

    def __lt__(self, other: "FMVGraphEdge") -> bool:
        return str(self.predicate) < str(other.predicate)

    def __eq__(self, other: "FMVGraphEdge") -> bool:
        return str(self.predicate) == str(other.predicate)

    def __hash__(self):
        return hash((self.predicate, self.type_node))


class FMVGraphNode:
    _known_nodes = {}        # type: Dict[URIRef, 'FMVGraphNode']

    def __init__(self, g: Graph, node: URIRef) -> None:
        """
        Construct a directed graph rooted in node

        :param g: FHIR Metadata Vocabulary + w5
        :param node: URI of node
        """
        self.node: URIRef = node                            # URI of the node itself
        self.edges: List[FMVGraphEdge] = []                 # Outgoing edges
        self.parents: List["FMVGraphNode"] = []                     # Parent types
        FMVGraphNode._known_nodes[node]: Dict[URIRef, FMVGraphNode] = self  # Prevent recursive looping
        self.is_primitive: bool = is_primitive(g, node)

        if not self.is_primitive:
            self.is_complex_type = node in fhir_complex_types
            for sc in g.objects(node, RDFS.subClassOf):
                unionof_value = g.value(sc, OWL.unionOf)
                if unionof_value:
                    for union_sc in Collection(g, unionof_value):
                        predicate, _ = predicate_and_type_for(g, union_sc)
                        if predicate not in skip_fhir_predicates:
                            self.edges.append(FMVGraphEdge(g, union_sc))
                else:
                    for sc_type in g.objects(sc, RDF.type):
                        if sc_type == OWL.Restriction:
                            predicate, _ = predicate_and_type_for(g, sc)
                            if predicate not in skip_fhir_predicates:
                                self.edges.append(FMVGraphEdge(g, sc))
                        elif sc_type != OWL.Class:
                            self.edges += self._known_nodes[sc_type].edges \
                                if sc_type in FMVGraphNode._known_nodes else FMVGraphNode(g, sc_type).edges
                        else:
                            self.parents.append(self._known_nodes[sc]
                                                if sc in FMVGraphNode._known_nodes else FMVGraphNode(g, sc))
        else:
            self.is_complex_type = False

    def as_indented_str(self, indent: int=0, multiple_entries: bool = False) -> str:
        """
        Pretty-print node as an indented string
        :param indent: depth at this point
        :param multiple_entries: true means the cardinality > 1
        :return: indented string
        """
        modifiers = ("M" if multiple_entries else "") + ("P" if self.is_primitive else "") + \
                    ("C" if self.is_complex_type else "")
        return "({})".format(fns(self.node)) + ("({})".format(modifiers) if modifiers else "") + \
               ((':\n' + '\n'.join([e.as_indented_str(indent+1) for e in sorted(self.edges)])) if self.edges else "")

    def __str__(self) -> str:
        return self.as_indented_str()


class FHIRMetaDataVocabulary(FHIRMetaVoc):

    """
    FHIR Metadata Vocabulary - represents a combination of the FMV and W5 ontology
    """
    def __init__(self,
                 mv_file_loc: str="http://build.fhir.org/fhir.ttl",
                 w5_file_loc: str="http://build.fhir.org/w5.ttl",
                 fmt: str="turtle",
                 cache_mv_file=True):
        super().__init__(mv_file_loc, fmt, cache_mv_file)
        self.g.load(w5_file_loc, format=fmt)
        self.w5_graph = FHIRW5Ontology(self.g)

    def fhir_resource_concepts(self) -> Set[URIRef]:
        """
        Return the uris for the set of all qualifying FHIR resources
        :return: URIs of all FHIR resources
        """
        return {subj for subj in self.g.transitive_subjects(RDFS.subClassOf, FHIR.Resource)
                if isinstance(subj, URIRef) and not self.w5_graph.is_w5_infrastructure(subj)}

    def resource_graph(self, subject: URIRef) -> FMVGraphNode:
        return FMVGraphNode(self.g, subject)
