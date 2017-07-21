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
import re
from typing import Union, List, Optional, Dict
from urllib import request
from uuid import uuid4

from jsonasobj.jsonobj import JsonObj, loads
from rdflib import Graph, OWL, RDFS, RDF, XSD, URIRef, Namespace
from rdflib.term import Node, BNode, Literal

from i2fhirb2.fhir.fhirspecific import FHIR, FHIR_RESOURCE_RE, FHIR_RE_RESOURCE, FHIR_RE_BASE, \
    REPLACED_NARRATIVE_TEXT
from i2fhirb2.loaders.fhirmetavoc import FHIRMetaVoc
from i2fhirb2.rdfsupport.prettygraph import PrettyGraph

LOINC = Namespace("http://loinc.org/owl#")
SNOMEDCT = Namespace("http://snomed.info/id/")
# TODO: Figure the correct URI here
RXNORM = Namespace("http://www.nlm.nih.gov/research/umls/rxnorm")

namespaces = {"fhir": FHIR,
              "owl": OWL,
              "rdfs": RDFS,
              "rdf": RDF,
              "xsd": XSD}


def loinc_uri(_: str, code: str, nsmap: Dict[str, Namespace]) -> Optional[URIRef]:
    nsmap.setdefault('loinc', LOINC)
    return LOINC[code]


def snomed_uri(_: str, code: str, nsmap: Dict[str, Namespace]) -> Optional[URIRef]:
    nsmap.setdefault('sct', SNOMEDCT)
    return SNOMEDCT[code] if code.isdigit() else None


def hl7_v3_uri(system: str, code: str, nsmap: Dict[str, Namespace]) -> Optional[URIRef]:
    nsmap.setdefault('v3-' + system.replace('http://hl7.org/fhir/v3/', ''), Namespace(system))
    return URIRef(system + '/' + code)


def hl7_v2_uri(system: str, code: str, nsmap: Dict[str, Namespace]) -> Optional[URIRef]:
    nsmap.setdefault('v2-' + system.replace('http://hl7.org/fhir/v2/', ''), Namespace(system))
    return URIRef(system + '/' + code)


def hl7_fhir_uri(system: str, code: str, nsmap: Dict[str, Namespace]) -> Optional[URIRef]:
    nsmap.setdefault(system.replace('http://hl7.org/fhir/', ''), Namespace(system))
    return URIRef(system + '/' + code)


# Map from FHIR codesystem URI to generator
codesystem_maps = {"http://loinc.org": loinc_uri,
                   "http://snomed.info/sct": snomed_uri,
                   re.compile(r"http://hl7.org/fhir/v3/*"): hl7_v3_uri,
                   re.compile(r"http://hl7.org/fhir/v2/*"): hl7_v2_uri,
                   re.compile(r"http://hl7.org/fhir/[a-z-]+"): hl7_fhir_uri}


class FHIRResource:
    """ A FHIR RDF representation of a FHIR JSON resource """
    def __init__(self, vocabulary: Graph, json_fname: Optional[str], base_uri: str,
                 data: Optional[JsonObj]=None, target: Optional[Graph]=None, add_ontology_header: bool=True,
                 replace_narrative_text: bool=False):
        """
        Construct an RDF representation
        :param vocabulary: FHIR Metadata Vocabulary (fhir.ttl)
        :param json_fname: URI or file name of resource to convert
        :param base_uri: base of resource URI -- will be combined with the resource id to generate the actual URI
        :param data: if present load this data rather than json_fname
        :param target: target graph -- used for collections, bundles, etc.
        :param add_ontology_header: Add the OWL ontology header to the output
        :param replace_narrative_text: Replace long narrative text section with boilerplate
        """
        if json_fname:
            self.root = self.load_file_or_uri(json_fname)
        else:
            self.root = data
        self._base_uri = base_uri + ('/' if base_uri[-1] not in '/#' else '')
        if 'resourceType' not in self.root:
            raise ValueError("{} is not a FHIR resource".format(json_fname))
        if 'id' not in self.root:
            self.root.id = str(uuid4())
        self._resource_uri = URIRef(self._base_uri + self.root.resourceType + '/' + self.root.id)
        self._meta = FHIRMetaVoc(vocabulary, FHIR[self.root.resourceType])
        self._g = PrettyGraph() if target is None else target
        self._vocabulary = vocabulary
        self._addl_namespaces = dict()
        self._add_ontology_header = add_ontology_header
        self._replace_narrative_text = replace_narrative_text
        self.generate()

    @property
    def resource_id(self) -> Optional[str]:
        resource_id_container = self._g.value(self._resource_uri, FHIR.Resource.id)
        return self._g.value(resource_id_container, FHIR.value) if resource_id_container else None

    @property
    def resource_type(self) -> str:
        return self.root.resourceType

    @property
    def graph(self):
        return self._g

    @staticmethod
    # TODO: Determine whether this is still neededd
    def base_uri(full_uri: str, resource_id: Optional[str], resource_type: str) -> Optional[str]:
        """
        Determine the root of full_uri.  If full_uri matches the pattern:
        <base>/[resource_type][/|#]resource_id, return base else None
        :return: URI base if it can be termined

        :param full_uri: complete URI
        :param resource_id: resource id.  If not present, just strip [/|#]*
        :param resource_type: type
        :return:
        """
        if not resource_id:
            base_uri = full_uri.rsplit('#', 1)[0] if '#' in full_uri else \
                       full_uri.rsplit('/', 1)[0] if '/' in full_uri else \
                       None
        elif full_uri.endswith('#' + resource_id) or full_uri.endswith('/' + resource_id):
            base_uri = full_uri[:-len(resource_id) - 1]
        else:
            base_uri = None
        if base_uri is None or not base_uri.endswith('/' + resource_type):
            return None
        return base_uri[:-len(resource_type)]

    def add_prefixes(self, nsmap: Dict[str, Namespace]) -> None:
        """
        Add the required prefix definitions
        :return:
        """
        [self._g.bind(e[0], e[1]) for e in nsmap.items()]

    def add_ontology_definition(self) -> None:
        ont_uri = URIRef(str(self._resource_uri) + ".ttl")
        self.add(ont_uri, RDF.type, OWL.Ontology)\
            .add(ont_uri, OWL.imports, FHIR['fhir.ttl'])
        if 'meta' in self.root and 'versionId' in self.root.meta:
            self.add(ont_uri, OWL.versionIRI, URIRef(str(ont_uri) + '/_history/' + self.root.meta.versionId))

    def add(self, subj: Node, pred: URIRef, obj: Node) -> "FHIRResource":
        """
        Shortcut to rdflib add function
        :param subj:
        :param pred:
        :param obj:
        :return: self for chaining
        """
        self._g.add((subj, pred, obj))
        return self

    def add_value_node(self, subj: Node, pred: URIRef, val: Union[JsonObj, str, List],
                       valuetype: Optional[URIRef]= None) -> "FHIRResource":
        """
        Expand val according to the range of pred and add it to the graph
        :param subj: graph subject
        :param pred: graph predicate
        :param val: JSON representation of target object
        :param valuetype: predicate type if it can't be directly determined
        :return: self for chaining
        """
        val_meta = FHIRMetaVoc(self._vocabulary, self._meta.predicate_type(pred) if not valuetype else valuetype)
        for k, p in val_meta.predicates().items():
            if k in val:
                self.add_val(subj, p, val[k])
                if pred == FHIR.CodeableConcept.coding:
                    self.add_type_arc(subj, val)
            elif k == "value" and val_meta.predicate_type(p) == FHIR.Element:
                # value / Element is the wild card combination -- if there is a "value[x]" in val, emit it where the
                # type comes from 'x'
                for vk in val._as_dict.keys():
                    if vk.startswith(k):
                        self.add_val(subj, FHIR[vk], val[vk], FHIR[vk[len(k):]])
        return self

    def add_reference(self, subj: Node, val: str) -> "FHIRResource":
        """
        Add a fhir:link and RDF type arc if it can be determined
        :param subj: reference subject
        :param val: reference value
        :return: self for chaining
        """
        match = FHIR_RESOURCE_RE.match(val)
        ref_uri_str = res_type = None
        if match:
            ref_uri_str = val if match.group(FHIR_RE_BASE) else (self._base_uri + val)
            res_type = match.group(FHIR_RE_RESOURCE)
        elif self._base_uri and not val.startswith('#') and not val.startswith('/'):
            ref_uri_str = self._base_uri + val
            res_type = val.split('/', 1)[0] if '/' in val else "Resource"
        if ref_uri_str:
            ref_uri = URIRef(ref_uri_str)
            self.add(subj, FHIR.link, ref_uri)
            self.add(ref_uri, RDF.type, FHIR[res_type])
        return self

    def add_type_arc(self, subj: Node, val: JsonObj) -> None:
        if "system" in val and "code" in val:
            for k in codesystem_maps.keys():
                if (isinstance(k, str) and k == val.system) or (not isinstance(k, str) and k.match(val.system)):
                    type_uri = codesystem_maps[k](val.system, val.code, self._addl_namespaces)
                    if type_uri:
                        self.add(subj, RDF.type, type_uri)
                    break

    def add_val(self, subj: Node, pred: URIRef, val: Union[JsonObj, str, List],
                valuetype: Optional[URIRef] = None) -> "FHIRResource":
        """
        Add the RDF representation of val to the graph as a target of subj, pred.  Note that FHIR lists are
        represented as a list of BNODE objects with a fhir:index discrimanant
        :param subj: graph subject
        :param pred: predicate
        :param val: value to be expanded
        :param valuetype: value type if NOT determinable by predicate
        :return: self for chaining
        """
        if isinstance(val, List):
            list_idx = 0
            for lv in val:
                entry_bnode = BNode()
                self.add(entry_bnode, FHIR['index'], Literal(list_idx))\
                    .add_value_node(entry_bnode, pred, lv, valuetype)\
                    .add(subj, pred, entry_bnode)
                list_idx += 1
        else:
            vt = self._meta.predicate_type(pred) if not valuetype else valuetype
            if self._meta.is_atom(vt):
                if self._replace_narrative_text and pred == FHIR.Narrative.div and len(val) > 120:
                    val = REPLACED_NARRATIVE_TEXT
                self.add(subj, pred, Literal(val))
            else:
                v = BNode()
                if self._meta.is_primitive(vt):
                    self.add(v, FHIR.value, Literal(str(val), datatype=self._meta.primitive_datatype_nostring(vt, val)))
                else:
                    self.add_value_node(v, pred, val, valuetype)
                self.add(subj, pred, v)
                if pred == FHIR.Reference.reference:
                    self.add_reference(subj, val)
        return self

    def generate(self) -> Graph:
        self.add_prefixes(namespaces)
        if self._add_ontology_header:
            self.add_ontology_definition()
        self.add(self._resource_uri, RDF.type, FHIR[self.root.resourceType])
        self.add(self._resource_uri, FHIR.nodeRole, FHIR.treeRoot)
        for k, p in self._meta.predicates().items():
            if k in self.root:
                self.add_val(self._resource_uri, p, self.root[k])
        self.add_prefixes(self._addl_namespaces)
        return self._g

    @staticmethod
    # TODO: move this capability back to jsonasobj package
    def load_file_or_uri(name: str) -> JsonObj:
        if '://' in name:
            with request.urlopen(name) as response:
                jsons = response.read()
        else:
            with open(name) as f:
                jsons = f.read()
        return loads(jsons)

    def __str__(self):
        return self._g.serialize().decode()
