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
from typing import Optional, List, cast, Callable

from rdflib import URIRef, RDFS
from rdflib.namespace import split_uri

from i2fhirb2.fhir.fhirmetadata import FHIRMetadata
from i2fhirb2.fhir.fhirspecific import concept_code, concept_path, W5, w5_infrastructure_categories
from i2fhirb2.i2b2model.i2b2ontology import OntologyEntry, OntologyRoot, ConceptOntologyEntry, ModifierOntologyEntry


class FHIROntologyTable(FHIRMetadata):
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
            for path in self.i2b2_paths(self._name_base, subj, RDFS.subClassOf):
                rval.append(ConceptOntologyEntry(subj, path, path, False, False))

        for subj in self.fhir_concepts(subject):
            for path in self.i2b2_paths(self._name_base, subj, RDFS.subClassOf, self.is_w5_path):
                if '.' not in split_uri(subj)[1]:
                    # TODO: find a semantic way to resolve this -- lexical parsing is brittle
                    rval.append(ConceptOntologyEntry(subj, path, path, False))
                # Add an entry for each property of the subject
                for prop in self.concept_properties(subj):
                    for obj in self.g.objects(prop, RDFS.range):
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
        for range_obj in self.g.objects(prop, RDFS.range):
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

    def i2b2_paths(self, base: str, subject: URIRef, predicate: URIRef,
                   filtr: Optional[Callable[[List[URIRef]], bool]] = None) -> [str]:
        rval = []
        for path in self.full_paths(subject, predicate):
            if not filtr or filtr(path):
                rval.append(base + (''.join(concept_path(e) for e in path[:-1])))
        return rval

    def full_paths(self, subject: URIRef, predicate: URIRef) -> List[List[URIRef]]:
        parents = [obj for obj in self.g.objects(subject, predicate) if isinstance(obj, URIRef)]
        if not parents:
            rval = [[subject]]
        else:
            rval = []
            for parent in parents:
                for e in self.full_paths(parent, predicate):
                    e.append(subject)
                    rval.append(e)
        return rval

    @staticmethod
    def is_w5_path(path: List[URIRef]) -> bool:
        """
        Determine whether path represents a primary w5 path.  This exists to remove the alternate
        paths that culminate in fhir:Thing.
        :param path: path to test
        :return: True if it is a single length path (e.g. Patient.status) or has a non-skipped w5
        category in its ancestors.
        """
        if len(path) > 1:
            if split_uri(path[0])[0] != str(W5):
                return False
        return not bool(set(path).intersection(w5_infrastructure_categories))

    @staticmethod
    def tsv_header() -> str:
        return OntologyEntry._header()
