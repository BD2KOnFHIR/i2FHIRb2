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
from typing import Union, Dict, List, Optional

from jsonasobj.jsonobj import load, JsonObj
from rdflib import Graph, OWL, RDFS, RDF, XSD, Namespace, URIRef
from rdflib.term import Node, BNode, Literal

FHIR = Namespace("http://hl7.org/fhir/")
W5 = Namespace("http://hl7.org/w5#")

namespaces = {"fhir": FHIR,
              "owl": OWL,
              "rdfs": RDFS,
              "rdf": RDF,
              "xsd": XSD}


class FHIRMeta:
    """
    FHIR "ontology" representation for a given subject
    """
    def __init__(self, ontology: Graph, subject: Union[str, URIRef]):
        """
        Represent FHIR metadata for subject
        :param ontology: FHIR "ontology" (fhir.ttl)
        :param subject: name or URI of subject in ontology
        """
        self._o = ontology
        self._subj = subject if isinstance(subject, URIRef) else URIRef(FHIR[subject])

    @staticmethod
    def _to_str(uri: URIRef) -> str:
        """
        Convert a FHIR style URI into a tag name to be used to retrieve data from a JSON representation
        Example: http://hl7.org/fhir/Provenance.agent.whoReference --> whoReference
        :param uri: URI to convert
        :return: tag name
        """
        local_name = str(uri).replace(str(FHIR), '')
        return local_name.rsplit('.', 1)[1] if '.' in local_name else local_name

    def predicates(self) -> Dict[str, URIRef]:
        """
        Return the tag names and corresponding URI's for all properties that can be associated with subject
        :return: Map from tag name (JSON object identifier) to corresponding URI
        """
        rval = dict()
        for parent in self._o.objects(self._subj, RDFS.subClassOf):
            if isinstance(parent, URIRef) and not str(parent).startswith(str(W5)):
                rval.update(**FHIRMeta(self._o, parent).predicates())
        for s in self._o.subjects(RDFS.domain, self._subj):
            rval[self._to_str(s)] = s
        return rval

    def predicate_type(self, pred: URIRef) -> URIRef:
        """
        Return the type of pred
        :param pred: predicate to map
        :return:
        """
        return self._o.value(pred, RDFS.range)

    def is_primitive(self, t: URIRef) -> bool:
        """
        Determine whether type "t" is a FHIR primitive type
        :param t: type to test
        :return:
        """
        return FHIR.Primitive in self._o.objects(t, RDFS.subClassOf)

    def is_atom(self, t: URIRef) -> bool:
        """
        Determine whether type "t" is an 'atomic' type -- i.e it doesn't use a FHIR value representation
        :param t: type to test
        :return:
        """
        return len(set(self._o.objects(t, RDFS.subClassOf))) == 0

    def primitive_datatype(self, t: URIRef) -> Optional[URIRef]:
        """
        Return the data type for primitive type t, if any
        :param t: type
        :return: corresponding data type
        """
        for sco in self._o.objects(t, RDFS.subClassOf):
            sco_type = self._o.value(sco, RDF.type)
            sco_prop = self._o.value(sco, OWL.onProperty)
            if sco_type == OWL.Restriction and sco_prop == FHIR.value:
                return self._o.value(sco, OWL.allValuesFrom)
        return None

    def primitive_datatype_nostring(self, t: URIRef) -> Optional[URIRef]:
        """
        Return the data type for primitive type t, if any, defaulting string to no type
        :param t: type
        :return: corresponding data type
        """
        vt = self.primitive_datatype(t)
        return None if vt == XSD.string else vt

class FHIRRDF:
    """ A FHIR RDF representation of a FHIR JSON resource """
    def __init__(self, vocabulary: Graph, json_fname: str, resource_uri: str):
        """
        Construct an RDF representation
        :param vocabulary: FHIR Metadata Vocabulary (fhir.ttl)
        :param json_fname: URI or file name of resource to convert
        :param resource_uri: URI of resource (Will be changed later
        """
        with open(json_fname) as f:
            self.root = load(f)
        self._g = Graph()
        self._vocabulary = vocabulary
        self._uri = URIRef(resource_uri)
        self._meta = FHIRMeta(vocabulary, FHIR[self.root.resourceType])
        self.generate()

    def add_prefixes(self) -> None:
        """
        Add the required prefix definitions
        :return:
        """
        [self._g.bind(e[0], e[1]) for e in namespaces.items()]

    def add(self, subj: Node, pred: URIRef, obj: Node) -> "FHIRRDF":
        """
        Shortcut to rdflib add function
        :param subj:
        :param pred:
        :param obj:
        :return: self for chaining
        """
        self._g.add((subj, pred, obj))
        return self

    def add_node(self, subj: Node, pred: URIRef, val: Union[JsonObj, str, List]) -> "FHIRRDF":
        """
        Expand val according to the range of pred and add it to the graph
        :param subj: graph subject
        :param pred: graph predicate
        :param val: JSON representation of target object
        :return: self for chaining
        """
        val_meta = FHIRMeta(self._vocabulary, self._meta.predicate_type(pred))
        for k, p in val_meta.predicates().items():
            if k in val:
                self.add_val(subj, p, val[k])
        return self

    def add_val(self, subj: Node, pred: URIRef, val: Union[JsonObj, str, List]) -> "FHIRRDF":
        """
        Add the RDF representation of val to the graph as a target of subj, pred.  Note that FHIR lists are
        represented as a list of BNODE objects with a fhir:index discrimanant
        :param subj: graph subject
        :param pred: predicate
        :param val: value to be expanded
        :return: self for chaining
        """
        if isinstance(val, List):
            list_idx = 0
            for lv in val:
                entry_bnode = BNode()
                self.add(entry_bnode, FHIR['index'], Literal(list_idx))\
                    .add_node(entry_bnode, pred, lv)\
                    .add(subj, pred, entry_bnode)
                list_idx += 1
        else:
            vt = self._meta.predicate_type(pred)
            if self._meta.is_atom(vt):
                self.add(subj, pred, Literal(val))
            else:
                v = BNode()
                if self._meta.is_primitive(vt):
                    self.add(v, FHIR.value, Literal(val, datatype=self._meta.primitive_datatype_nostring(vt)))
                else:
                    self.add_node(v, pred, val)
                self.add(subj, pred, v)
        return self

    def generate(self) -> Graph:
        self.add_prefixes()
        self.add(self._uri, RDF.type, FHIR[self.root.resourceType])
        self.add(self._uri, FHIR.nodeRole, FHIR.treeRoot)
        for k, p in self._meta.predicates().items():
            if k in self.root:
                self.add_val(self._uri, p, self.root[k])
        return self._g

    def serialize(self) -> str:
        return self._g.serialize(format="turtle").decode("utf-8")
