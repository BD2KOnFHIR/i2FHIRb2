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
from datetime import datetime
from typing import List, Optional, Union

from fhirtordf.rdfsupport.namespaces import FHIR
from rdflib import URIRef, Graph, BNode, RDF, XSD
from rdflib.term import Node, Literal

from i2fhirb2.fhir.fhircodemapping import coded_predicates, proc_observation_component
from i2fhirb2.fhir.fhirencountermapping import FHIREncounterMapping
from i2fhirb2.fhir.fhirpatientdimension import FHIRPatientDimension
from i2fhirb2.fhir.fhirpatientmapping import FHIRPatientMapping
from i2fhirb2.fhir.fhirproviderdimension import FHIRProviderDimension
from i2fhirb2.fhir.fhirspecific import concept_code, composite_uri, instance_is_primitive
from i2fhirb2.fhir.fhirvisitdimension import FHIRVisitDimension
from i2fhirb2.i2b2model.data.i2b2observationfact import ObservationFact, ObservationFactKey, valuetype_blob, \
    valuetype_text, valuetype_date, valuetype_number
from i2fhirb2.sqlsupport.dynobject import DynElements

# TODO: Same patient_ide/patient_ide_src + visit_ide / visit_ide_src == duplicate


def literal_val(val: Literal) -> str:
    return '"{}"'.format(str(val).replace('\n', '\\n').replace(r'\t', '\\t'))


def boolean_val(val: Literal) -> str:
    return val.value


def date_val(val: Literal) -> datetime:
    return val.value


def datetime_val(val: Literal) -> datetime:
    return datetime.strptime(val.value, '%Y-%m-%dT%H:%M:%SZ')


def decimal_val(val: Literal) -> float:
    return float(val.value)


def gyear_val(val: Literal) -> datetime:
    return datetime.strptime(val.value, '%Y')


def gYearMonth_val(val: Literal) -> datetime:
    return datetime.strptime(val.value, '%Y-%m')


def time_val(val: Literal) -> datetime:
    return datetime.strptime(val.value, '%H:%M:%S')


# Conversion table from XSD data type to corresponding i2b2 field
literal_conversions = {
    XSD.base64Binary: (literal_val, valuetype_blob),
    XSD.boolean: (boolean_val, valuetype_text),
    XSD.date: (date_val, valuetype_date),
    XSD.dateTime: (datetime_val, valuetype_date),
    XSD.decimal: (decimal_val, valuetype_number),
    XSD.gYear: (gyear_val, valuetype_date),
    XSD.gYearMonth: (gYearMonth_val, valuetype_date),
    XSD.integer: (decimal_val, valuetype_number),
    XSD.nonNegativeInteger: (decimal_val, valuetype_number),
    XSD.positiveInteger: (decimal_val, valuetype_number),
    XSD.time: (time_val, valuetype_date)}


class FHIRObservationFact(ObservationFact):
    _t = DynElements(ObservationFact)

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
        super().__init__(ofk, concept_code(concept) if isinstance(concept, URIRef) else concept)
        if modifier is not None:
            self._modifier_cd = concept_code(modifier)
        self._instance_num = instance_num
        if obj is not None:
            self.fhir_primitive(g, obj)
        self.identifying_codes: List[str] = []

    def fhir_primitive(self, g: Graph, obj: Optional[Node]) -> None:
        assert(instance_is_primitive(g, obj))
        val = g.value(obj, FHIR.value, any=False)
        # TODO: remove the conversions that aren't needed (toPython does the same thing)
        if val.datatype in literal_conversions:
            f, t = literal_conversions[val.datatype]
            if t == valuetype_text:
                self._tval_char = val.toPython()
            elif t == valuetype_number:
                self._tval_char = 'E'
                self._nval_num = val.toPython()
            elif t == valuetype_blob:
                self._observation_blob = val.toPython()
            elif t == valuetype_date:
                dt = val.toPython()
                self._date_val(dt)
            else:
                self._tval_char = val.toPython()
            self._valtype_cd = t.code
        else:
            self._tval_char = val.toPython()
            self._valtype_cd = valuetype_text.code


class FHIRObservationFactFactory:
    """
    FHIRObservationFactFactory takes an RDF graph and generates a set of observation_fact, patient_dimension,
    visit_dimension, provider_dimension, patient_mapping and encounter_mapping entries
    """

    # TODO: FHIR.Observation.referenceRange predicates are a temporary fix to issue 7.  Get a real fix in!
    special_processing_list = {RDF.type: None, FHIR.nodeRole: None, FHIR.index: None, FHIR.link: None,
                               FHIR.Observation.referenceRange: None}

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
        :param subject: Subject of the observation (Patient)
        :return:
        """
        rval = []               # type: List[FHIRObservationFact]

        identifying_codes = []
        for conc, obj in sorted(self.g.predicate_objects(subject)):
            if conc not in self.special_processing_list:
                if conc in coded_predicates:
                    coded_facts = coded_predicates[conc](self.g, subject, self.ofk)
                    identifying_codes = [e.concept_cd for e in coded_facts]
                    rval += coded_facts

                if instance_is_primitive(self.g, obj):
                    rval.append(FHIRObservationFact(self.g, self.ofk, conc, None, obj))
                else:
                    rval += self.generate_modifiers(subject, conc, obj, identifying_codes=identifying_codes)

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
            sorted([(p, o) for p, o in self.g.predicate_objects(obj) if p not in self.special_processing_list])

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
        # TODO: Generalize
        if fhir_index is not None and concept == FHIR.Observation.component:
            rval += proc_observation_component(self.g, obj, self.ofk, inst_num, identifying_codes)
        return rval
