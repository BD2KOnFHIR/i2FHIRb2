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

from i2fhirb2.fhir.fhirspecific import FHIR, i2b2_paths, concept_path, skip_w5_categories, is_w5_path, is_w5_uri
from i2fhirb2.i2b2model.i2b2conceptdimension import ConceptDimension, ConceptDimensionRoot
from i2fhirb2.i2b2model.i2b2modifierdimension import ModifierDimension
from i2fhirb2.i2b2model.i2b2ontology import OntologyEntry, ConceptOntologyEntry, ModifierOntologyEntry, OntologyRoot


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
                if isinstance(subj, URIRef) and is_w5_uri(subj) and subj not in skip_w5_categories}

    def fhir_resource_concepts(self) -> Set[URIRef]:
        """
        Return the uris for the set of all qualifying FHIR resources
        :return:
        """
        rval = set()
        for c in self.transitive_subjects(RDFS.subClassOf, FHIR.DomainResource):
            if isinstance(c, URIRef):
                if not set(self.transitive_objects(c, RDFS.subClassOf)).intersection(skip_w5_categories):
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
        return {s for s in self.subjects(RDFS.domain, subj)
                if not any(e for e in self.objects(s, RDFS.subPropertyOf) if not is_w5_uri(e))}

    def dimension_list(self, subj: Optional[URIRef]=None) -> List[OntologyEntry]:
        """ Abstract class to return i2b2 dimension entries"""
        return []

    @staticmethod
    def tsv_header() -> str:
        """ Abstract class to return i2b2 dimension tsv header"""
        return ""


class FHIRConceptDimension(FHIROntology):
    """ A list of all FHIR resources, as identified by the DomainResource tag """
    def dimension_list(self, subject: Optional[URIRef]=None) -> List[ConceptDimension]:
        return [cast(ConceptDimension, ConceptDimensionRoot('FHIR'))] + \
               [ConceptDimension(subj, self._name_base)
                for subj in self.w5_concepts().union(self.fhir_concepts(subject))]

    @staticmethod
    def tsv_header() -> str:
        return ConceptDimension._header()


class FHIRModifierDimension(FHIROntology):
    """ A list of all FHIR predicates. """
    def dimension_list(self, _: Optional[URIRef]=None) -> List[ModifierDimension]:
        # TODO: Include references as modifiers (e.g. \FHIR\Patient\managingOrganization\
        # subject is ignored -- too hard to determine dependences for a modifier
        conc_dimension = self.fhir_concepts()
        return [ModifierDimension(subj, self._name_base) for subj in self.subjects(RDF.type, OWL.ObjectProperty)
                if subj not in conc_dimension]

    @staticmethod
    def tsv_header() -> str:
        return ModifierDimension._header()


class FHIROntologyTable(FHIROntology):
    """  The set of i2b2 ontology table entries for the supplied subject or all root concepts
    """

    def is_primitive(self, obj) -> bool:
        return not self.value(obj, RDFS.subClassOf, None) or obj in {FHIR.Reference}

    def dimension_list(self, subject: Optional[URIRef]=None) -> List[OntologyEntry]:
        """
        Return the set of ontology entries for all w5 concepts and resources
        :param subject: Optional subject -- for debugging purposes only
        :return: List of i2b2 ontology entries
        """
        rval = [cast(OntologyEntry, OntologyRoot('FHIR'))]

        for subj in self.w5_concepts():
            for path in i2b2_paths(self._name_base, self, subj, RDFS.subClassOf):
                rval.append(ConceptOntologyEntry(subj, path, path, False))

        for subj in self.fhir_concepts(subject):
            for path in i2b2_paths(self._name_base, self, subj, RDFS.subClassOf, is_w5_path):
                rval.append(ConceptOntologyEntry(subj, path, path, False))
                # Add an entry for each property of the subject
                for prop in self.concept_properties(subj):
                    for obj in self.objects(prop, RDFS.range):
                        if self.is_primitive(obj):
                            # Primitive type -- enter as a modifier and continue
                            entry = ModifierOntologyEntry(1,
                                                          subj,
                                                          prop,
                                                          path + concept_path(subj),
                                                          self._name_base,
                                                          True,
                                                          obj)
                        else:
                            # Nested type -- first level becomes a concept, the remainder will be classes
                            entry = ConceptOntologyEntry(prop,
                                                         path,
                                                         self._name_base,
                                                         False)
                            rval += self.modifiers(subj, prop, entry.c_fullname, self._name_base)
                        rval.append(entry)

        return rval

    def modifiers(self,
                  subj: URIRef,
                  prop: URIRef,
                  full_concept_path: str,
                  modifier_base_path: str,
                  depth: int=1,
                  nested: bool=False) -> List[ModifierOntologyEntry]:
        rval = []
        for obj in self.objects(prop, RDFS.range):

            # Primitives and primitive-like objects
            if self.is_primitive(obj):
                rval.append(ModifierOntologyEntry(depth, subj, prop, full_concept_path, modifier_base_path, True, obj))

            # Recursion checkpoint - shouldn't happen - filter with the obj not in below
            elif depth > 7:
                raise Exception("Recursion error")

            # Non-primitive - extend the path to all of the leaf nodes.
            elif obj not in {FHIR.TermComponent, FHIR.Extension, FHIR.Meta}:
                if nested:
                    rval.append(ModifierOntologyEntry(depth, obj, prop, full_concept_path, modifier_base_path, False))
                for obj_prop in self.concept_properties(obj):
                    rval += self.modifiers(obj,
                                           obj_prop,
                                           full_concept_path,
                                           modifier_base_path,
                                           (depth+1) if nested else depth, True)
            else:
                pass            # debug point

        return rval

    @staticmethod
    def tsv_header() -> str:
        return OntologyEntry._header()
