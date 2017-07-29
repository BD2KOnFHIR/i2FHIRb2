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
from typing import Set, Optional, List

from i2fhirb2.i2b2model.metadata.i2b2conceptdimension import ConceptDimension
from rdflib import Graph, URIRef, RDF, OWL, RDFS
from rdflib.namespace import split_uri

from i2fhirb2.fhir.fhirspecific import FHIR, skip_fhir_predicates, w5_infrastructure_categories, W5, fhir_primitives
from i2fhirb2.i2b2model.metadata.i2b2modifierdimension import ModifierDimension
from i2fhirb2.i2b2model.metadata.i2b2ontology import OntologyEntry


class ModifierPath:
    """
    Structure for carrying information about a modifier and its depth
    """
    def __init__(self, hlevel: int, fullname: URIRef, dimcode: URIRef, type_: URIRef):
        """
        Ontology c_hlevel, c_fullnmae, c_dimcode combination for modifier entry
        :param hlevel:  depth
        :param fullname: URI of full path
        :param dimcode:  URI for type
        :param type_: target type
        """
        self.hlevel = hlevel
        self.fullname = fullname
        self.dimcode = dimcode
        self.type = type_


class FHIRMetadata(metaclass=ABCMeta):
    """
    The W5 OntologyEntry in i2b2 space
    """

    def __init__(self, g: Graph, name_base: str = "\\FHIR\\"):
        """
        Create a FHIR i2b2 generator
        :param g: Graph containing fhir.ttl information
        :param name_base: Base for concept_dimension / modifier_dimension and non-modifier ontology paths
        """
        assert(name_base.endswith('\\'))
        self.g = g
        self._name_base = name_base
        ConceptDimension.graph = g
        ModifierDimension.graph = g
        OntologyEntry.graph = g

    def w5_concepts(self) -> Set[URIRef]:
        """
        Return the uris for the w5 (classification) classes. These become the i2b2 navigational concepts.
        """
        return {subj for subj in self.g.subjects(RDF.type, OWL.Class)
                if isinstance(subj, URIRef) and self.is_w5_uri(subj) and not self.w5_infrastructure_category(subj)}

    def w5_infrastructure_category(self, subj: URIRef) -> bool:
        """
        Determine whether subj belongs to a w5 infrastructure category
        :param subj: FHIR Element
        :return:
        """
        return bool(set(self.g.transitive_objects(subj, RDFS.subClassOf)).intersection(w5_infrastructure_categories))

    def fhir_resource_concepts(self) -> Set[URIRef]:
        """
        Return the uris for the set of all qualifying FHIR resources
        :return:
        """
        return {subj for subj in self.g.transitive_subjects(RDFS.subClassOf, FHIR.Resource)
                if isinstance(subj, URIRef) and not self.w5_infrastructure_category(subj)}

    def fhir_concepts(self, subject: Optional[URIRef]=None) -> Set[URIRef]:
        """
        Return all qualifying descendants of fhir:Resource + all first level properties.  This is the complete
        set of FHIR elements in the concept dimension.
        :param subject: Subject to restrict output to for debugging
        :return:
        """
        rval = set()
        for subj in ({subject} if subject else self.fhir_resource_concepts()):
            rval.add(subj)
            rval.update(self.concept_properties(subj))
        return rval

    def concept_properties(self, subj: URIRef) -> Set[URIRef]:
        """
        Return all of the properties for a given subject.  Note that FHIR generates a separate property
        for each element of a choice. As an example, "value" has a separate entry for "valueBoolean", "valueInteger",
        "valueDate", etc.  For the time being, we skip entries that are subproperties of parent FHIR
        (but not W5) elements.
        :param subj: subject class
        :return: list of associated properties property predicates
        """
        # TODO: Temporary fix for putting together the poster
        return {s for s in self.g.subjects(RDFS.domain, subj)}
        # if not any(e for e in self.objects(s, RDFS.subPropertyOf) if not is_w5_uri(e))}

    def dimension_list(self, _: Optional[URIRef]=None) -> List[OntologyEntry]:
        """ Abstract class to return i2b2 dimension entries"""
        return []

    def is_primitive(self, subj: URIRef) -> bool:
        """
        Determine whether subj is 'primitive' in the FHIR context
        :param subj:
        :return:
        """
        parents = set(self.g.objects(subj, RDFS.subClassOf))
        return not parents or FHIR.Primitive in parents or subj in fhir_primitives

    def skipped_v5_domain(self, pred: URIRef) -> bool:
        """
        Return true if the domain of pred falls in a skipped domain
        :param pred: p
        :return:
        """
        for dom in self.g.objects(pred, RDFS.domain):
            if self.w5_infrastructure_category(dom):
                return True
        return False

    def value_property(self, prop) -> Optional[URIRef]:
        """
        Determine whether prop is one of the [x]'s in value[x]
        :param prop: predicate to test
        :return: base value property if it is an '[x]' type
        """
        # TODO: Make this work correctly
        return None
        # super_prop = self.value(prop, RDFS.subPropertyOf)
        # TODO: We need to upgrade the ontology to provide a semantic way to do this
        # return super_prop if super_prop and str(super_prop).endswith(".value") else None

    def generate_modifier_path(self, prop: URIRef, range_type: URIRef, depth: int=1,
                               seen: Optional[Set[URIRef]]=None) -> List[ModifierPath]:
        """
        Generate a list of URI's that represent the transitive closure of prop's predicates
        :param prop: Root property
        :param range_type: Element in the range of root property (typically only one)
        :param depth: Nesting depth
        :param seen: List of things we've looked at. Used to prevent infinite recursion.
        :return: List of modifier paths derived from prop and range_type
        """
        rval = []               # type: List[ModifierPath]
        if seen is None:
            seen = set()
        for pred in self.g.subjects(RDFS.domain, range_type):
            if pred not in skip_fhir_predicates:
                # Concatenate the root property and predicates in the nested range
                extended_prop = self.composite_uri(prop, pred)
                for rng in self.g.objects(pred, RDFS.range):
                    if rng not in seen:
                        seen.add(rng)
                        rval.append(ModifierPath(depth, extended_prop, pred, rng))
                        if not self.is_primitive(rng):
                            rval += self.generate_modifier_path(extended_prop, rng, depth+1, seen)
                        seen.discard(rng)
        return rval

    @staticmethod
    def composite_uri(parent: URIRef, mod: URIRef) -> URIRef:
        """
        Return a composite URI consisting of the parent + '.' + the last element in the modifier
        :param parent: base URI
        :param mod: modifier URI
        :return: composite
        """
        p1 = split_uri(mod)
        if len(p1) < 2:
            print("E1")
        p2 = p1[1].rsplit('.', 1)
        if len(p2) < 2:
            print("E2")
        last_mod_component = split_uri(mod)[1].rsplit('.', 1)[1]
        return URIRef(str(parent) + '.' + last_mod_component)

    @staticmethod
    def is_w5_uri(uri: URIRef) -> bool:
        return split_uri(uri)[0] == str(W5)

    @staticmethod
    @abstractmethod
    def tsv_header() -> str:
        """ Abstract class to return i2b2 dimension tsv header"""
        return ""
