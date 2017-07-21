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
from typing import Optional, TextIO, Tuple

from rdflib import URIRef, Graph, OWL, RDF, Namespace
from rdflib.compare import to_isomorphic, graph_diff
from rdflib.term import Identifier, BNode, Node

from i2fhirb2.fhir.fhirspecific import FHIR
from i2fhirb2.rdfsupport.prettygraph import PrettyGraph


def skolem_bnode(s: URIRef, p: URIRef, idx: int) -> URIRef:
    return URIRef(str(s) + '.' + str(p).rsplit('/', 1)[1] + "_{}".format(idx))


def map_node(s: BNode, sk_s: URIRef, gin: Graph, gout: Graph, iter_idx: int) -> int:
    for p, o in gin.predicate_objects(s):
        if not isinstance(o, BNode):
            gout.add((sk_s, p, o))
        else:
            idx = gin.value(o, FHIR['index'])
            if idx is None:
                if len([o for o in gin.objects(s, p) if isinstance(o, BNode)]) == 1:
                    idx = 0
                else:
                    idx = iter_idx
                    iter_idx += 1
            sk_o = skolem_bnode(sk_s, p, idx)
            gout.add((sk_s, p, sk_o))
            iter_idx = map_node(o, sk_o, gin, gout, iter_idx)
    return iter_idx


def skolemize(gin: Graph) -> Graph:
    gout = Graph()
    iter_idx = 1001
    for (s, p, o) in gin:
        if isinstance(s, URIRef):
            if not isinstance(o, BNode):
                gout.add((s, p, o))
            else:
                idx = gin.value(o, FHIR['index'])
                if idx is None:
                    if len([o for o in gin.objects(s, p) if isinstance(o, BNode)]) == 1:
                        idx = 0
                    else:
                        idx = iter_idx
                        iter_idx += 1
                sk_o = skolem_bnode(s, p, idx)
                gout.add((s, p, sk_o))
                iter_idx = map_node(o, sk_o, gin, gout, iter_idx)
    return gout


def complete_definition(subj: Identifier,
                        source_graph: Graph,
                        target_graph: Optional[Graph]=None) -> PrettyGraph:
    """
    Return the full definition for the supplied subject, following any object bnodes
    :param subj: URI or BNode for subject
    :param source_graph: Graph containing defininition
    :param target_graph: return graph (for recursion)
    :return: target_graph
    """
    if target_graph is None:
        target_graph = PrettyGraph()
    for p, o in source_graph.predicate_objects(subj):
        target_graph.add((subj, p, o))
        if isinstance(o, BNode):
            complete_definition(o, source_graph, target_graph)
    return target_graph


def dump_nt_sorted(g):
    for l in sorted(g.serialize(format='nt').splitlines()):
        if l:
            print(l.decode('ascii'))


def rdf_compare(g1: Graph, g2: Graph, diffs_file: Optional[TextIO] = None, ignore_owl_version: bool=False,
                ignore_type_arcs:bool = False) -> bool:
    def p(txt: str, **args) -> None:
        if diffs_file:
            print(txt, file=diffs_file, **args)

    success = True
    g1_subjs = set([s for s in g1.subjects() if isinstance(s, URIRef)])
    g2_subjs = set([s for s in g2.subjects() if isinstance(s, URIRef)])
    for s in g1_subjs - g2_subjs:
        p("\nMISSED: ", end='')
        print(PrettyGraph.strip_prefixes(complete_definition(s, g1)))
        success = False
    for s in g2_subjs - g1_subjs:
        print("\nADDED: ", end='')
        print(PrettyGraph.strip_prefixes(complete_definition(s, g2)))
        success = False
    for s in g1_subjs.intersection(g2_subjs):
        s_in_g1 = complete_definition(s, g1)
        s_in_g2 = complete_definition(s, g2)
        if ignore_type_arcs:
            for g1s, g1o in s_in_g1.subject_objects(RDF.type):
                if isinstance(g1s, BNode) and isinstance(g1o, URIRef):
                    s_in_g1.remove((g1s, RDF.type, g1o))
            for g2s, g2o in s_in_g2.subject_objects(RDF.type):
                if isinstance(g2s, BNode) and isinstance(g2o, URIRef):
                    s_in_g2.remove((g2s, RDF.type, g2o))
        if ignore_owl_version:
            if s_in_g1.value(s, OWL.versionIRI):
                s_in_g1.remove((s, OWL.versionIRI, s_in_g1.value(s, OWL.versionIRI)))
            if s_in_g2.value(s, OWL.versionIRI):
                s_in_g2.remove((s, OWL.versionIRI, s_in_g2.value(s, OWL.versionIRI)))
        in_both, in_first, in_second = graph_diff(skolemize(s_in_g1), skolemize(s_in_g2))
        if len(in_first) or len(in_second):
            p("\n{} DIFFERENCE: ".format(s) + '=' * 30)
            if len(in_first):
                p("\tFirst: ")
                dump_nt_sorted(in_first)
            if len(in_second):
                p("\tSecond: ")
                dump_nt_sorted(in_second)
            print('-' * 40)
            success = False
    return success
