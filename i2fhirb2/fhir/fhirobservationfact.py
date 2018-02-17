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
from typing import List, Optional, Union, Tuple

from fhirtordf.rdfsupport.namespaces import FHIR
from rdflib import URIRef, Graph, BNode, RDF
from rdflib.term import Node

from i2fhirb2.fhir.fhircodemapping import process_concept_code
from i2fhirb2.fhir.fhirencountermapping import FHIREncounterMapping
from i2fhirb2.fhir.fhirnamespaces import fhir_namespace_for
from i2fhirb2.fhir.fhirpatientdimension import FHIRPatientDimension
from i2fhirb2.fhir.fhirpatientmapping import FHIRPatientMapping
from i2fhirb2.fhir.fhirprimitivetypes import i2b2_primitive, I2B2Value
from i2fhirb2.fhir.fhirproviderdimension import FHIRProviderDimension
from i2fhirb2.fhir.fhirspecific import composite_uri, instance_is_primitive
from i2fhirb2.fhir.fhirvisitdimension import FHIRVisitDimension
from i2fhirb2.i2b2model.data.i2b2observationfact import ObservationFact, ObservationFactKey
from i2fhirb2.sqlsupport.dynobject import DynElements


# TODO: Same patient_ide/patient_ide_src + visit_ide / visit_ide_src == duplicate


class FHIRObservationFact(ObservationFact):

    _unknown_namespaces: List[str] = []         # URI's that have been reported as being unknown

    def __init__(self, g: Graph, ofk: ObservationFactKey, concept: Union[URIRef, str],
                 modifier: Optional[Union[URIRef, str]], obj: Optional[Node],
                 instance_num: Optional[int] = None) -> None:
        """
        Construct an observation fact entry
        :param g: Graph containing information about the object
        :param ofk: Observation fact key - patient, encounter, etc
        :param concept: concept URI
        :param modifier: modifier URI (if any)
        :param obj: object of concept_code
        :param instance_num: instance identifier
        """
        super().__init__(ofk, self.ns_name_for(concept) if isinstance(concept, URIRef) else concept)
        if modifier is not None:
            self._modifier_cd = self.ns_name_for(modifier)
        self._instance_num = instance_num
        if obj is not None:
            v: I2B2Value = i2b2_primitive(g.value(obj, FHIR.value, any=False))
            self._valtype_cd = v.valtype
            self._tval_char = v.tval_char
            self._nval_num = v.nval_num
            self._observation_blob = v.observation_blob
        self.identifying_codes: List[str] = []

    @classmethod
    def ns_name_for(cls, concept_uri: Union[URIRef, str]) -> Optional[str]:
        """ Convert concept_uri into a NS:code construct if the namespace is known

        :param concept_uri: URI to convert
        :return: NS:code representation if NS is known, else None
        """
        concept_uri = str(concept_uri)
        if '#' in concept_uri:
            nsuri, cd = concept_uri.rsplit('#', 1)
            nsuri += '#'
        else:
            nsuri, cd = concept_uri.rsplit('/', 1)
            nsuri += '/'
        ns = fhir_namespace_for(nsuri)
        if ns is None:
            if nsuri not in cls._unknown_namespaces:
                cls._unknown_namespaces.append(nsuri)
                print(f"----> Unrecognized namespace: {nsuri}\n")
            return None

        ns = ns.upper()
        # Some FHIR resources seem to include the namespace as part of the code (?)
        return cd if cd.startswith(ns + ':') else ns.upper() + ':' + cd

    @classmethod
    def _clear(cls, complete=True):
        cls._unknown_namespaces = []
        ObservationFact._clear(complete)


class FHIRObservationFactFactory:
    """
    FHIRObservationFactFactory takes an RDF graph and generates a set of observation_fact, patient_dimension,
    visit_dimension, provider_dimension, patient_mapping and encounter_mapping entries
    """

    # List of predicates to be ignored in primary node generation
    # TODO: FHIR.Observation.referenceRange predicates are a temporary fix to issue 7.  Get a real fix in
    skip_predicates = [RDF.type, FHIR.nodeRole, FHIR.index, FHIR.link, FHIR.Observation.referenceRange]

    def __init__(self, g: Graph, ofk: ObservationFactKey, subject: Optional[URIRef]) -> None:
        self.g = g
        self.ofk = ofk
        self.observation_facts: List[FHIRObservationFact] = []
        self.patient_dimensions: List[FHIRPatientDimension] = []
        self.provider_dimensions: List[FHIRProviderDimension] = []
        self.visit_dimensions: List[FHIRVisitDimension] = []
        self.patient_mappings: List[FHIRPatientMapping] = []
        self.encounter_mappings: List[FHIREncounterMapping] = []
        self._inst_num = 0

        # TODO: look at DomainResource embedded entries (claim-example-oral-bridge).  Perhaps we should change the
        #       RDF generator to add type arcs to all resources?
        for s in {subject} if subject else self.g.subjects(FHIR.nodeRole, FHIR.treeRoot):
            self.observation_facts += self.generate_facts(s)

    def generate_facts(self, subject: URIRef) -> List[FHIRObservationFact]:
        """
        Generate an observation fact entry for each predicate object associated with subject.  If the predicate
        is not primitive (i.e. it has a non-value BNode as a target), generate a series of modifiers for each element
        in the BNode.  Note -- this generation sorts the inputs because the order is indirectly preserved in the output
        instance numbers.

        :param subject: Resource subject
        :return: List of observation facts for subject
        """
        rval: List[FHIRObservationFact] = []            # List of observation facts to add
        identifying_codes: List[str] = []               # Identifying code(s) for this type of entry
        for conc, obj in sorted(self.g.predicate_objects(subject)):
            if conc not in self.skip_predicates:
                coded_facts = process_concept_code(self.g, subject, subject, conc, self.ofk)
                if coded_facts:
                    identifying_codes = [e.concept_cd for e in coded_facts]
                    rval += coded_facts

                if instance_is_primitive(self.g, obj):
                    # The presence of a type arc on a primitive node indicates a code -- the value will be recorded
                    # elsewhere
                    if not self.g.value(obj, RDF.type):
                        rval.append(FHIRObservationFact(self.g, self.ofk, conc, None, obj))
                else:
                    rval += self.generate_modifiers(subject, conc, obj, identifying_codes=identifying_codes)
            elif conc == RDF.type:
                rval.append(FHIRObservationFact(self.g, self.ofk, obj, None, None))

        return self.removeduplicates(rval)

    @staticmethod
    def removeduplicates(facts: List[FHIRObservationFact]) -> List[FHIRObservationFact]:
        """ The process of adding modifiers can result in more than one subject concept_cd for the same value.  As an
        example, visionprescription-example-1.ttl.html has two products that are dispensed, both of which are contacts.

        :param facts: List of facts to be pruned
        :return: List with duplicates removed
        """
        fact_keys: List[Tuple[int, str, str]] = []
        rval: List[FHIRObservationFact] = []
        for fact in facts:
            k = (fact.instance_num, fact.concept_cd, fact.modifier_cd)
            if k not in fact_keys:
                fact_keys.append(k)
                rval.append(fact)
        return rval

    def generate_modifiers(self, subject: URIRef, concept: URIRef, obj: BNode,
                           parent_inst_num: int=0, same_subject: bool=False,
                           identifying_codes: Optional[List[str]]=None) -> List[FHIRObservationFact]:
        """
        Emit any modifiers for subject/obj.  If there is fhir:index field, this is an indication that this set
        of modifiers can occur multiple times and, as such, must be clustered.  Noting that, at the moment, we
        can only do one level of clustering, we do not generate unique instance numbers for singleton elements.

        :param subject: Resource subject
        :param concept: Concept identifier (first level entry)
        :param obj: inner cluster (usually a BNODE)
        :param parent_inst_num: instance number passed in recursive call
        :param same_subject: True means same parent -- don't revisit instance number
        :param identifying_codes: Code(s) assigned to the element
        :return:
        """
        rval = []               # type: List[FHIRObservationFact]
        fhir_index = self.g.value(obj, FHIR.index, any=False) if not same_subject else None
        pred_obj_list = \
            sorted([(p, o) for p, o in self.g.predicate_objects(obj) if p not in self.skip_predicates])

        if fhir_index is not None and len(pred_obj_list):
            self._inst_num += 1
            inst_num = self._inst_num
        else:
            inst_num = parent_inst_num

        for modifier, modifier_object in pred_obj_list:
            if instance_is_primitive(self.g, modifier_object):
                mod_inst_idx = self.g.value(modifier_object, FHIR.index, any=False)
                if mod_inst_idx is not None and len(pred_obj_list) > 1:
                    self._inst_num += 1
                    inst_num = self._inst_num
                obsfact = FHIRObservationFact(self.g, self.ofk, concept, modifier, modifier_object, inst_num)
                rval.append(obsfact)
            else:
                rval += self.generate_modifiers(subject,
                                                concept if inst_num else composite_uri(concept, modifier),
                                                modifier_object,
                                                inst_num,
                                                same_subject=True,
                                                identifying_codes=identifying_codes)
            rval += process_concept_code(self.g, concept, obj, modifier, self.ofk, inst_num, identifying_codes)
        return rval
