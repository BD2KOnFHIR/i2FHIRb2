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
from typing import List, Set, Optional, cast

from rdflib import Graph, RDFS, RDF, OWL, URIRef
from rdflib.namespace import split_uri

from i2fhirb2.fhir.fhirspecific import FHIR, i2b2_paths, w5_infrastructure_category, is_w5_path, is_w5_uri, \
    concept_code, recursive_fhir_types, skip_fhir_predicates, composite_modifier
from i2fhirb2.i2b2model.i2b2conceptdimension import ConceptDimension, ConceptDimensionRoot
from i2fhirb2.i2b2model.i2b2modifierdimension import ModifierDimension
from i2fhirb2.i2b2model.i2b2ontology import OntologyEntry, ConceptOntologyEntry, ModifierOntologyEntry, OntologyRoot


class ModifierPath:
    def __init__(self, predicate: URIRef, depth: int, typ: URIRef):
        self.predicate = predicate
        self.depth = depth
        self.type = typ


class FHIROntology(Graph):
    """
    The W5 OntologyEntry in i2b2 space
    """

    def __init__(self, *args, name_base: str="\\FHIR\\", **kwargs):
        """
        Create a FHIR i2b2 generator
        :param args: args for Graph constructor
        :param name_base: Base for concept_dimension / modifier_dimension and non-modifier ontology paths
        :param kwargs: args for Graph constructor
        """
        super().__init__(*args, **kwargs)
        assert(name_base.endswith('\\'))
        self._name_base = name_base
        ConceptDimension.graph = self
        ModifierDimension.graph = self
        OntologyEntry.graph = self

    def w5_concepts(self) -> Set[URIRef]:
        """
        Return the uris for the w5 (classification) classes. This becomes the i2b2 navigational concepts
        """
        return {subj for subj in self.subjects(RDF.type, OWL.Class)
                if isinstance(subj, URIRef) and is_w5_uri(subj) and not w5_infrastructure_category(self, subj)}

    def fhir_resource_concepts(self) -> Set[URIRef]:
        """
        Return the uris for the set of all qualifying FHIR resources
        :return:
        """
        rval = set()
        for c in self.transitive_subjects(RDFS.subClassOf, FHIR.DomainResource):
            if isinstance(c, URIRef):
                if not w5_infrastructure_category(self, c):
                    rval.add(c)
        return rval

    def fhir_concepts(self, subject: Optional[URIRef]=None) -> Set[URIRef]:
        """
        Return all qualifying descendants of fhir:DomainResource + all first level properties.  This is the complete
        set of FHIR elements in the concept dimension.
        :param subject: subject to restrict output to
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
        return {s for s in self.subjects(RDFS.domain, subj)}
                # if not any(e for e in self.objects(s, RDFS.subPropertyOf) if not is_w5_uri(e))}

    def dimension_list(self, subj: Optional[URIRef]=None) -> List[OntologyEntry]:
        """ Abstract class to return i2b2 dimension entries"""
        return []

    def is_primitive(self, obj) -> bool:
        return self.value(obj, RDFS.subClassOf, None) is None or obj in {FHIR.Reference}

    def skipped_v5_domain(self, pred: URIRef) -> bool:
        """
        Return true if the domain of pred falls in a skipped domain
        :param pred: p
        :return:
        """
        for dom in self.objects(pred, RDFS.domain):
            if w5_infrastructure_category(self, dom):
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
        super_prop = self.value(prop, RDFS.subPropertyOf)
        # TODO: We need to upgrade the ontology to provide a semantic way to do this
        return super_prop if super_prop and str(super_prop).endswith(".value") else None

    def generate_modifier_path(self, prop: URIRef, range_type: URIRef, depth: int=1,
                               seen: Optional[List[URIRef]]=None) -> List[ModifierPath]:
        """
        Generate a list of URI's that represent the transitive closure of prop's predicates
        :param prop: URI if root property
        :param range_type: URI of a range or prop
        :param depth: Nesting depth
        :param seen: list of things we've looked at. Recursion prevention
        :return: list of all URI's included in prop
        """
        rval = []               # type: List[ModifierPath]
        if seen is None:
            seen = []
        seen.append(range_type)
        for pred in self.subjects(RDFS.domain, range_type):
            if pred not in skip_fhir_predicates:
                # Take the concept code of the range, remove the first element before the '.'
                # Sometimes the last part of the property matches the first part of the range
                # (e.g. Observation.component.referenceRange + Observation.referenceRange.type)  When this occurs,
                # remove the redundant element
                extended_prop = composite_modifier(prop, pred)
                for rng in self.objects(pred, RDFS.range):
                    rval.append(ModifierPath(extended_prop, depth, rng))
                    # TODO: Is this a bug in the interpreter?
                    if rng not in seen:
                        if not self.is_primitive(rng):
                            rval += self.generate_modifier_path(extended_prop, rng, depth+1, seen)
        assert(seen.pop()==range_type)
        return rval

    @staticmethod
    def tsv_header() -> str:
        """ Abstract class to return i2b2 dimension tsv header"""
        return ""


class FHIRConceptDimension(FHIROntology):
    """ A list of all FHIR resources, as identified by the DomainResource tag """
    def dimension_list(self, subject: Optional[URIRef]=None) -> List[ConceptDimension]:
        return [cast(ConceptDimension, ConceptDimensionRoot('FHIR'))] + \
               [ConceptDimension(subj, self._name_base)
                for subj in self.fhir_concepts(subject)]

    @staticmethod
    def tsv_header() -> str:
        return ConceptDimension._header()


class FHIRModifierDimension(FHIROntology):
    """ A list of all FHIR predicates. """

    def dimension_list(self, _: Optional[URIRef]=None, domain: Optional[URIRef]=None) -> List[ModifierDimension]:
        """
        Return the complete set of modifiers in the ontology
        :param _: subject - used for testing and ignored here
        :param domain: restrict to properties in this domain (e.g. FHIR.CodeableConcept)
        :return: list of modifiers
        """
        # TODO: Include references as modifiers (e.g. \FHIR\Patient\managingOrganization\
        rval = []               # type: List[ModifierDimension]
        value_added = False     # If we're in the value[x] space, add one element, 'value'
        conc_dimension = self.fhir_concepts()
        properties = self.subjects(RDFS.domain, domain) if domain else self.subjects(RDF.type, OWL.ObjectProperty)
        for prop in properties:
            if prop not in conc_dimension and not self.skipped_v5_domain(prop):
                vp = self.value_property(prop)
                if vp:
                    if not value_added:
                        rval.append(ModifierDimension(vp, self._name_base))
                        value_added = True
                else:
                    rval.append(ModifierDimension(prop, self._name_base))
                    for range_ in self.objects(prop, RDFS.range):
                        if not self.is_primitive(range_) and \
                                        range_ not in recursive_fhir_types:
                            rval += self.extend_modifier_path(prop, range_)
        return rval

    def extend_modifier_path(self, prop: URIRef, range_type: URIRef) -> List[ModifierDimension]:
        """
        Synthesize a URI for embedded paths (e.g. CodeableConcept.coding.[Coding].system)
        :param prop: Base URI
        :param range_type: URI of range
        :return:
        """
        return [ModifierDimension(p.predicate, self._name_base) for p in self.generate_modifier_path(prop, range_type)]

    @staticmethod
    def tsv_header() -> str:
        return ModifierDimension._header()


class FHIROntologyTable(FHIROntology):
    """  The set of i2b2 ontology table entries for the supplied subject or all root concepts
    """

    def dimension_list(self, subject: Optional[URIRef]=None) -> List[OntologyEntry]:
        """
        Return the set of ontology entries for all w5 concepts and resources
        :param subject: Optional subject -- for debugging purposes only
        :return: List of i2b2 ontology entries
        """
        rval = [cast(OntologyEntry, OntologyRoot('FHIR'))]

        for subj in self.w5_concepts():
            for path in i2b2_paths(self._name_base, self, subj, RDFS.subClassOf):
                rval.append(ConceptOntologyEntry(subj, path, path, False, False))

        for subj in self.fhir_concepts(subject):
            for path in i2b2_paths(self._name_base, self, subj, RDFS.subClassOf, is_w5_path):
                if '.' not in split_uri(subj)[1]:
                    # TODO: find a semantic way to resolve this -- lexical parsing is brittle
                    rval.append(ConceptOntologyEntry(subj, path, path, False))
                # Add an entry for each property of the subject
                for prop in self.concept_properties(subj):
                    for obj in self.objects(prop, RDFS.range):
                        if self.is_primitive(obj):
                            # Primitive type -- Can be accessed with a single code
                            entry = ConceptOntologyEntry(prop,
                                                         path,
                                                         self._name_base,
                                                         True,
                                                         True,
                                                         obj)
                        else:
                            # Nested type -- first level becomes a concept, the remainder will be classes
                            entry = ConceptOntologyEntry(prop,
                                                         path,
                                                         self._name_base,
                                                         False,
                                                         '.' in concept_code(prop))
                            rval += self.modifiers(subj, prop, entry.c_fullname, self._name_base)
                        rval.append(entry)

        return rval

    def modifiers(self, subj: URIRef, prop: URIRef, full_concept_path: str, modifier_base_path: str,
                  depth: int=1) -> List[ModifierOntologyEntry]:
        rval = []
        value_added = False
        for range_obj in self.objects(prop, RDFS.range):
            vp = self.value_property(prop)
            if vp:
                if not value_added:
                    rval.append(ModifierOntologyEntry(depth, subj, prop, full_concept_path, modifier_base_path, True,
                                                      vp))
                    value_added = True
            elif self.is_primitive(range_obj):
                rval.append(ModifierOntologyEntry(depth, subj, prop, full_concept_path, modifier_base_path, True,
                                                  range_obj))
            else:
                recursive_modifiers = self.generate_modifier_path(prop, range_obj)
                for rm in recursive_modifiers:
                    rval.append(ModifierOntologyEntry(rm.depth, subj, rm.predicate, full_concept_path,
                                                      modifier_base_path, self.is_primitive(rm.type), rm.type))
        return rval

    @staticmethod
    def tsv_header() -> str:
        return OntologyEntry._header()
