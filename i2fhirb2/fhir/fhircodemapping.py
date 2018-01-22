# Copyright (c) 2018, Mayo Clinic
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
from typing import List, Dict, Callable, Optional

from fhirtordf.rdfsupport.namespaces import FHIR
from fhirtordf.rdfsupport import fhirgraphutils
from rdflib import URIRef, Graph, RDF
from rdflib.term import Node, Literal

from i2fhirb2.fhir.fhirspecific import concept_code
from i2fhirb2.i2b2model.data.i2b2observationfact import ObservationFactKey, ObservationFact, valuetype_text, \
    valuetype_number, valuetype_novalue


def value_string(g: Graph, subject: Literal, obs_fact: ObservationFact) -> None:
    obs_fact._valtype_cd = valuetype_text
    obs_fact._tval_char = fhirgraphutils.value(g, subject, FHIR.string)


comparator_map = {'<': 'L',
                  '<=': 'LE',
                  '>=': 'GE',
                  '>': 'G'}


def value_quantity(g: Graph, subject: Node, obs_fact: ObservationFact) -> None:
    # def value(g: Graph, subject: Node, predicate: URIRef, asLiteral=False) -> \
    #         Union[None, BNode, URIRef, str, date, bool, datetime, int, float]:
    units = fhirgraphutils.value(g, subject, FHIR.Quantity.unit)
    comparator = fhirgraphutils.value(g, subject, FHIR.Quantity.comparator)
    value = fhirgraphutils.value(g, subject, FHIR.Quantity.value)
    if value is not None:
        obs_fact._valtype_cd = valuetype_number
        obs_fact._nval_num = value
        obs_fact._tval_char = 'E' if comparator is None else comparator_map.get(str(comparator), '?')
        obs_fact._units_cd = str(units)
    else:
        obs_fact._valtype_cd = valuetype_novalue


def value_integer(g: Graph, subject: Literal, obs_fact: ObservationFact) -> None:
    obs_fact._valtype_cd = valuetype_number
    obs_fact._nval_num = fhirgraphutils.value(g, subject, FHIR.integer)
    obs_fact._tval_char = 'E'


def value_codeable_concept(g: Graph, subject: Node, obs_fact: ObservationFact) -> None:
    coding = g.value(subject, FHIR.CodeableConcept.coding)
    if coding is not None:
        code = g.value(coding, RDF.type)
        if code:
            obs_fact._modifier_cd = concept_code(code)
    text = fhirgraphutils.value(g, subject, FHIR.CodeableConcept.text)
    if text:
        obs_fact._valtype_cd = valuetype_text
        obs_fact._tval_char = text


value_processors: Dict[str, Callable[[Graph, Node, ObservationFact], None]] = {
    "valueQuantity": value_quantity,
    "valueCodeableConcept": None,
    "valueString": value_string,
    "valueBoolean": None,
    "valueInteger": value_integer,
    "valueRange": None,
    "valueRatio": None,
    "valueSampledData": None,
    "valueTime": None,
    "valueDateTime": None,
    "valuePeriod": None
}


def proc_value_node(g: Graph, obs_fact, predicate: URIRef, object: Node) -> None:
    # TODO: Interpretation
    value_type = str(predicate).split('.')[-1]
    if value_type not in value_processors:
        raise NotImplementedError(f"Unrecognized value type: {value_type}")
    if value_processors[value_type] is not None:
        value_processors[value_type](g, object, obs_fact)


def proc_observation_component(g: Graph, subject: Node, ofk: ObservationFactKey, inst_num: int, 
                               identifying_codes: Optional[List[str]]) -> List[ObservationFact]:
    # TODO: Highly redundant code
    from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact
    rval: List[ObservationFact] = []
    codeable_concept = g.value(subject, FHIR.Observation.component.code, any=False)
    if codeable_concept:
        for coding in g.objects(codeable_concept, FHIR.CodeableConcept.coding):
            concept_code_coding = g.value(coding, RDF.type)
            coded_fact = FHIRObservationFact(g, ofk, concept_code_coding, None, None, instance_num=inst_num)
            for p, o in g.predicate_objects(subject):
                if str(p).startswith(str(FHIR)):
                    vtype = str(p).split('.')[-1]
                    if vtype.startswith('value'):
                        proc_value_node(g, coded_fact, p, o)
            rval.append(coded_fact)
            for id_code in identifying_codes:
                coded_fact_2 = FHIRObservationFact(g, ofk, id_code, concept_code_coding, None, instance_num=inst_num)
                for p, o in g.predicate_objects(subject):
                    if str(p).startswith(str(FHIR)):
                        vtype = str(p).split('.')[-1]
                        if vtype.startswith('value'):
                            proc_value_node(g, coded_fact_2, p, o)
                rval.append(coded_fact_2)

    return rval


def observation_concept_code(g: Graph,
                             subject: Node,
                             ofk: ObservationFactKey) -> List[ObservationFact]:
    from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact
    rval: List[ObservationFact] = []
    codeable_concept = g.value(subject, FHIR.Observation.code, any=False)
    if codeable_concept:
        for coding in g.objects(codeable_concept, FHIR.CodeableConcept.coding):
            concept_code_coding = g.value(coding, RDF.type)
            coded_fact = FHIRObservationFact(g, ofk, concept_code_coding, None, None)
            for p, o in g.predicate_objects(subject):
                if str(p).startswith(str(FHIR)):
                    vtype = str(p).split('.')[-1]
                    if vtype.startswith('value'):
                        proc_value_node(g, coded_fact, p, o)
            rval.append(coded_fact)
    return rval


coded_predicates: Dict[URIRef, Callable[[Graph, Node, ObservationFactKey], List]] = {
    FHIR.Observation.code: observation_concept_code}
