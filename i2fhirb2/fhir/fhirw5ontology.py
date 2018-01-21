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
from typing import Set, List, Optional

from fhirtordf.rdfsupport.namespaces import W5
from rdflib import Graph, URIRef, RDF, RDFS, OWL

from i2fhirb2.common_cli_parameters import DEFAULT_NAME_BASE
from i2fhirb2.fhir.fhirspecific import w5_infrastructure_categories, concept_path

INDENT = '  '


def is_w5_uri(uri: URIRef) -> bool:
    """ Determine whether uri is in the w5 namespace

    :param uri: URI to test
    :return: True if in w5 namespace
    """
    return str(uri).startswith(str(W5))


class W5GraphNode:
    """
    A node and all of the descendants down to and including the first non-w5 entry
    """
    def __init__(self, g: Graph, node: URIRef) -> None:
        self.node = node
        self.children = [W5GraphNode(g, subj) for subj in g.subjects(RDFS.subClassOf, node)
                         if isinstance(subj, URIRef)] if is_w5_uri(node) else []

    def indented_str(self, indent: int) -> str:
        rval = INDENT * indent + ('Node: {}' if is_w5_uri(self.node) else 'Resource: {}').format(self.node)
        if self.children:
            rval += '\n' + '\n'.join([c.indented_str(indent + 1) for c in sorted(self.children)])
        return rval

    def __str__(self) -> str:
        return self.indented_str(0)

    def __lt__(self, other: "W5GraphNode") -> bool:
        return self.node < other.node

    def __eq__(self, other: "W5GraphNode") -> bool:
        return self.node == other.node


class W5PathEntry:
    def __init__(self, path: str, w5_ent: W5GraphNode) -> None:
        """ A w5 path and accompanying metadata

        :param path: Full path to referenced node
        :param w5_ent: Corresponding W5GraphNode
        """
        self.node = w5_ent.node
        self.path = path
        self.fhir_resource_uri = self.node if not is_w5_uri(w5_ent.node) else None

    def __lt__(self, other) -> bool:
        return self.path < other.path

    def __eq__(self, other):
        return self.path == other.path

    def __str__(self) -> str:
        return self.path + (":({})".format(self.fhir_resource_uri) if self.fhir_resource_uri else "")


class FHIRW5Ontology:
    def __init__(self, g: Graph) -> None:
        """ A representation of the FHIR W5 GRAPH

        :param g: Graph containing W5 concepts
        """
        self.g = g
        self.w5_graph = [W5GraphNode(g, subj) for subj in self._w5_concepts() if g.value(subj, RDFS.subClassOf) is None]

    def _w5_concepts(self) -> Set[URIRef]:
        """
        Return a list of all W5 classes that aren't infrastructure classes
        """
        return {subj for subj in self.g.subjects(RDF.type, OWL.Class)
                if isinstance(subj, URIRef) and is_w5_uri(subj) and not self.is_w5_infrastructure(subj)}

    def is_w5_infrastructure(self, subj: URIRef) -> bool:
        """
        Determine whether subj belongs to a w5 infrastructure category
        :param subj: FHIR Element
        :return: True if this is an infrastructure category, false otherwise
        """
        return subj in w5_infrastructure_categories or \
            bool(set(self.g.transitive_objects(subj, RDFS.subClassOf)).intersection(w5_infrastructure_categories))

    def _nested_path(self, base: str, w5_ent: W5GraphNode) -> List[W5PathEntry]:
        node_path = base + concept_path(w5_ent.node)
        rval = [W5PathEntry(node_path, w5_ent)]
        for child in w5_ent.children:
            rval += self._nested_path(node_path, child)
        return rval

    def w5_paths(self, name_base: Optional[str] = DEFAULT_NAME_BASE) -> List[W5PathEntry]:
        rval = []
        for w5_ent in self.w5_graph:
            rval += self._nested_path(name_base, w5_ent)
        return rval

    def __str__(self):
        return "W5 Ontology\n" + '\n'.join([c.indented_str(1) for c in sorted(self.w5_graph)])
