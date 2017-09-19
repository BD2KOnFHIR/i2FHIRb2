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
from collections import OrderedDict
from typing import Set, Optional, List, Dict, Tuple

from fhirtordf.rdfsupport.namespaces import FHIR

from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFactFactory
from i2fhirb2.i2b2model.metadata.i2b2conceptdimension import ConceptDimension
from rdflib import Graph, URIRef, RDF, OWL, RDFS

from i2fhirb2.fhir.fhirspecific import w5_infrastructure_categories, fhir_primitives, composite_uri, is_w5_uri
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

    # fhir_concepts is a map from a concept_code URI to a tuple consisting of:
    #   a type URI -- for generating modifier entries in the ontology table
    #   a parent URI if the concept URI is not in the FHIR meta vocabulary
    _fhir_concepts = OrderedDict()  # type: Dict[URIRef, Tuple[URIRef, Optional[URIRef]]]

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
                if isinstance(subj, URIRef) and is_w5_uri(subj) and not self.w5_infrastructure_category(subj)}

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
        :return: URIs of all FHIR resources
        """
        return {subj for subj in self.g.transitive_subjects(RDFS.subClassOf, FHIR.Resource)
                if isinstance(subj, URIRef) and not self.w5_infrastructure_category(subj)}

    def fhir_concepts(self, resource: Optional[URIRef]=None) -> Dict[URIRef, Tuple[URIRef, Optional[URIRef]]]:
        """
        Return all qualifying descendants of fhir:Resource + all first level properties.  This is the complete
        set of FHIR elements in the concept dimension.
        :param resource: Subject to restrict output to for debugging
        :return: A list of all URI
        """
        if not self._fhir_concepts:
            for subj in ({resource} if resource else sorted(self.fhir_resource_concepts())):
                self._fhir_concepts[subj] = (None, None)        # No type / no parent
                self._generate_fact_concepts(subj)
        return self._fhir_concepts

    def _generate_fact_concepts(self, resource: URIRef) -> None:
        """
        Generate a concept entry for each predicate associated with subj.  This method parallels the generate_facts
        method in FHIRObservationFactFactory method.  The difference between the two is that, here, we generate a list
        of *all* possible concept codes, where the generate_facts method only generates those for things that exist.
        :param resource: URI of resource to concept
        """

        for concept_predicate in sorted(set(self.g.subjects(RDFS.domain, resource))):
            if concept_predicate not in FHIRObservationFactFactory.special_processing_list:
                range_type = self.g.value(concept_predicate, RDFS.range, any=False)
                self._fhir_concepts[concept_predicate] = (range_type, resource)
                if not self.is_primitive(range_type):
                    self._non_primitive_paths(concept_predicate, range_type)

    def _non_primitive_paths(self, base_predicate: URIRef, predicate_type: URIRef,
                             seen_predicate_types: List[URIRef] = None) -> None:

        if seen_predicate_types is None:
            seen_predicate_types = []
        if predicate_type not in seen_predicate_types:
            for predicate in sorted(set(self.g.subjects(RDFS.domain, predicate_type))):
                if predicate not in FHIRObservationFactFactory.special_processing_list:
                    range_type = self.g.value(predicate, RDFS.range, any=False)
                    if not self.is_primitive(range_type):
                        extended_base_predicate = composite_uri(base_predicate, predicate)
                        self._fhir_concepts[extended_base_predicate] = (range_type, base_predicate)
                        seen_predicate_types.append(predicate_type)
                        self._non_primitive_paths(extended_base_predicate, range_type, seen_predicate_types)
                        seen_predicate_types.remove(predicate_type)
        else:
            print("Recursion on :{} {}".format(base_predicate, predicate_type))

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
            if pred not in FHIRObservationFactFactory.special_processing_list:
                # Concatenate the root property and predicates in the nested range
                extended_prop = composite_uri(prop, pred)
                for rng in self.g.objects(pred, RDFS.range):
                    if rng not in seen:
                        seen.add(rng)
                        rval.append(ModifierPath(depth, extended_prop, pred, rng))
                        if not self.is_primitive(rng):
                            rval += self.generate_modifier_path(extended_prop, rng, depth+1, seen)
                        seen.discard(rng)
        return rval

    @staticmethod
    @abstractmethod
    def tsv_header() -> str:
        """ Abstract class to return i2b2 dimension tsv header"""
        return ""
