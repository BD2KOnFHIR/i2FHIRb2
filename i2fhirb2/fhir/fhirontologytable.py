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
from collections import OrderedDict
from typing import Optional, List, cast, Callable, Dict

from rdflib import URIRef, RDFS
from rdflib.namespace import split_uri

from i2fhirb2.fhir.fhirmetadata import FHIRMetadata
from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFactFactory
from i2fhirb2.fhir.fhirspecific import concept_path, W5, w5_infrastructure_categories, composite_uri, FHIR
from i2fhirb2.i2b2model.metadata.i2b2ontology import OntologyEntry, OntologyRoot, ConceptOntologyEntry, \
    ModifierOntologyEntry


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

        # fhir_concepts is an ordered dictionary whose keys are all concept_dimension concepts and
        # whose range is a tuple consisting of a type and an optional parent concept uri if the
        # concept isn't a root resource
        fhir_concepts = self.fhir_concepts(subject)
        base_paths = OrderedDict()          # type: Dict[URIRef, [str]]
        subj_parents = dict()               # type: Dict[URIRef, URIRef]

        # Determine all of the i2b2 paths to the root concepts
        for subj in fhir_concepts.keys():
            if fhir_concepts[subj][1] is None:
                base_paths[subj] = self.i2b2_paths(self._name_base, subj, RDFS.subClassOf, self.is_w5_path)
            else:
                subj_parents[subj] = fhir_concepts[subj][1]

        # Extend the paths to include the synthesized codes
        while subj_parents:
            parents_items = list(subj_parents.items())
            for subj, parent in parents_items:
                if parent in base_paths:
                    base_paths[subj] = base_paths[parent]
                    subj_parents.pop(subj)

        for subj in base_paths.keys():
            # Root resource code - non-leaf, non-draggable
            if fhir_concepts[subj][1] is None:
                for path in base_paths[subj]:
                    rval.append(ConceptOntologyEntry(subj, path, path, False, False))
            else:
                subj_type = fhir_concepts[subj][0]
                for path in base_paths[subj]:
                    if self.is_primitive(subj_type):
                        rval.append(ConceptOntologyEntry(subj, path, self._name_base, True, True, subj_type))
                    else:
                        rval.append(ConceptOntologyEntry(subj, path, self._name_base, False, True))
                        rval += self.modifiers_and_primitives(subj, subj_type, path)
        return rval

    def modifiers_and_primitives(self, subj: URIRef, subj_type: URIRef, path: str) -> List[OntologyEntry]:
        rval = []
        # Level 0 modifiers -- create an additional ConceptOntologyEntry for every primitive type
        # TODO: Facter this pattern out -- it appears in a lot of places
        pred_types = [(p, self.g.value(p, RDFS.range, any=False))
                      for p in self.g.subjects(RDFS.domain, subj_type)
                      if p not in FHIRObservationFactFactory.special_processing_list]
        for pred, pred_type in pred_types:
            if self.is_primitive(pred_type):
                rval.append(ModifierOntologyEntry(1,
                                                  subj,
                                                  pred,
                                                  path + concept_path(subj),
                                                  self._name_base,
                                                  self.is_primitive(pred_type),
                                                  pred,
                                                  pred_type if self.is_primitive(pred_type) else None))

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
