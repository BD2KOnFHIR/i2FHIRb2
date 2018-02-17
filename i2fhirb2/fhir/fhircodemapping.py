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
import copy
from typing import List, Dict, Callable, Optional

from fhirtordf.rdfsupport import fhirgraphutils
from fhirtordf.rdfsupport.namespaces import FHIR
from rdflib import URIRef, Graph, RDF
from rdflib.term import Node, Literal

from i2fhirb2.fhir.fhirnamespaces import fhir_namespace_for
from i2fhirb2.i2b2model.data.i2b2observationfact import ObservationFactKey, ObservationFact, valuetype_text, \
    valuetype_number, valuetype_novalue


def value_string(g: Graph, node: Node, obs_fact: ObservationFact) -> List[ObservationFact]:
    """ Convert a FHIR.string type value into the i2b2 equivalent

    :param g: Graph containing the data
    :param node: Node containing the string value
    :param obs_fact: target fact to have string added to it
    :return: Empty list - no additional facts are generated
    """
    obs_fact._valtype_cd = valuetype_text
    obs_fact._tval_char = g.value(node, FHIR.value, default=Literal(""), any=False).value
    return []


comparator_map = {'<': 'L',
                  '<=': 'LE',
                  '>=': 'GE',
                  '>': 'G'}


def value_quantity(g: Graph, subject: Node, obs_fact: ObservationFact) -> List[ObservationFact]:
    """ Process a FHIR:valueQuantity, recording salient information in obs_fact

    :param g: Graph containing the quantity
    :param subject: Subject of the fhir quantity node
    :param obs_fact: Fact to add the information to
    :return: Empty list - no additional facts are generated
    """
    units = fhirgraphutils.value(g, subject, FHIR.Quantity.unit)
    if not units:
        system = fhirgraphutils.value(g, subject, FHIR.Quantity.system)
        code = fhirgraphutils.value(g, subject, FHIR.Quantity.code)
        if code:
            ns = fhir_namespace_for(system)
            units = ((ns.upper() + ':') if ns else '') + code

    comparator = fhirgraphutils.value(g, subject, FHIR.Quantity.comparator)
    value_ = fhirgraphutils.value(g, subject, FHIR.Quantity.value)
    if value_ is not None:
        obs_fact._valtype_cd = valuetype_number
        obs_fact._nval_num = value_
        obs_fact._tval_char = 'E' if comparator is None else comparator_map.get(str(comparator), '?')
        obs_fact._units_cd = str(units) if units else None
    else:
        obs_fact._valtype_cd = valuetype_novalue
    return []


def value_integer(g: Graph, subject: Node, obs_fact: ObservationFact) -> List[ObservationFact]:
    """ Process a FHIR:valueInteger, recording salient information in obs_fact

    :param g: Graph containing the quantity
    :param subject: Subject of the fhir quantity node
    :param obs_fact: Fact to add the information to
    :return: Empty list - no additional facts are generated
    """
    obs_fact._valtype_cd = valuetype_number
    obs_fact._nval_num = g.value(subject, FHIR.value, any=False).value
    obs_fact._tval_char = 'E'
    return []


def value_codeable_concept(g: Graph, subject: Node, obs_fact: ObservationFact) -> List[ObservationFact]:
    """ Process a FHIR:valueCodeableConcept node.  The first FHIR:CodeableConcept.coding entry is recorded as
    the value for the passed `obs_fact`.  Additional obs_fact entries are generated to carry the text, if it exists,
    and any additional codings.

    :param g: Graph containing the data
    :param subject: CodeableConcept node
    :param obs_fact: target fact(s)
    :return: Additional obs_facts beyond obs_fact itself
    """
    from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact

    rval = []
    if obs_fact.modifier_cd != '@':
        print(f"{obs_fact.concept_cd}, {obs_fact.modifier_cd}: Modifier on modifier!")
    codings = sorted(list(g.objects(subject, FHIR.CodeableConcept.coding)))
    additional_entries = False
    if codings:
        for coding in codings:
            obs_fact_copy = copy.copy(obs_fact)
            if obs_fact.modifier_cd == '@':
                concept_uri = concept_uri_for(g, coding)
                concept_ns_name = FHIRObservationFact.ns_name_for(concept_uri) if concept_uri else None
                if concept_ns_name:
                    obs_fact._modifier_cd = concept_ns_name
            display = fhirgraphutils.value(g, coding, FHIR.Coding.display)
            if not display:
                display = fhirgraphutils.value(g, subject, FHIR.CodeableConcept.text)
            if display:
                obs_fact._valtype_cd = valuetype_text
                obs_fact._tval_char = display
                if additional_entries:
                    rval.append(obs_fact)
                else:
                    additional_entries = True
                obs_fact = obs_fact_copy
    else:
        text = fhirgraphutils.value(g, subject, FHIR.CodeableConcept.text)
        if text:
            obs_fact._valtype_cd = valuetype_text
            obs_fact._tval_char = text

    return rval


# Table of value types to i2b2 converters
value_processors: Dict[str, Callable[[Graph, Node, ObservationFact], List[ObservationFact]]] = {
    "valueQuantity": value_quantity,
    "valueCodeableConcept": value_codeable_concept,
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


def proc_value_node(g: Graph, obs_fact: ObservationFact, predicate: URIRef, object: Node) -> List[ObservationFact]:
    """ Process a value node, adding the value elements to obs_fact and returning a list of any additional facts
    that get generated in the process

    :param g:
    :param obs_fact: The primary fact to have values added to it
    :param predicate: The predicate (type) of value
    :param object: The target resource
    :return: Any additional observation facts *beyond* obs_fact
    """

    # TODO: Interpretation
    value_type = str(predicate).split('.')[-1]
    if value_type not in value_processors:
        raise NotImplementedError(f"Unrecognized value type: {value_type}")
    if value_processors[value_type] is not None:
        return value_processors[value_type](g, object, obs_fact)
    else:
        print(f"***> Unimplemented FHIR value: {value_type}")

    return []


def is_fhir_value(p: URIRef) -> bool:
    """ Determine whether `p` is a fhir:value[x] node

    :param p: predicate to test
    :return:
    """
    return str(p).startswith(str(FHIR)) and str(p).split('.')[-1].startswith('value')


def concept_uri_for(g: Graph, coding: Node) -> Optional[URIRef]:
    """ Return the URI for the concept in coding, if any.  If a type arc is present, it will be used.  Otherwise
    we will attempt to synthesize one from system and code.

    :param g: Graph containing the coding node
    :param coding: node that contains the FHIR.Coding entry
    :return: URI or None if nothing is available
    """
    uri = g.value(coding, RDF.type)
    if uri is None:
        # TODO: Combine this with the rules in fhirtordf - they should do exactly the same thing
        system = fhirgraphutils.value(g, coding, FHIR.Coding.system)
        code = fhirgraphutils.value(g, coding, FHIR.Coding.code)
        if system and code:
            uri = URIRef(system + ('' if system.endswith(('#', '/')) else '/') + code)
    return uri


def add_concept_values(g: Graph, obs_fact: ObservationFact, subject: URIRef, graph_node: Node) -> List[ObservationFact]:
    """  Add any value[x] entries to obs_fact

    :param g:
    :param obs_fact: Base fact
    :param subject: Subject of values
    :param graph_node: Node that may have value node predicates
    :return: Fact(s) with values added
    """
    rval = [obs_fact]
    if subject in code_value_tuples:
        # Add any associated value(s)
        for p, o in g.predicate_objects(graph_node):
            if is_fhir_value(p):
                rval += proc_value_node(g, obs_fact, p, o)
    elif str(subject).split('.')[-1] == "valueCodeableConcept":
        for o in g.objects(graph_node, subject):
            rval += proc_value_node(g, obs_fact, subject, o)
    return rval


def process_concept_code(g: Graph, root_concept: URIRef, subject: Node, predicate: URIRef, ofk: ObservationFactKey,
                         instance_num: Optional[int]=None, identifying_codes: Optional[List[str]]=None) \
        -> List[ObservationFact]:
    """ If predicate meets the requirements, emit additional facts that incorporate the referenced coded concept, using
    the following rules:
    1) If predicate occurs at the root level of a FHIR Resource:
        If predicate is marked as identifying, emit the referenced concept as a concept_cd
        Otherwise, emite predicate as the concept_cd and the referenced concept as a modifier_cd
    2) If the predicate occurs as a non-root (instance_num is not None), add the following entries:
            1) concept_cd = concept_code_coding, modifier_cd = '@' inst_num = 0
            2) concept_cd = identifying_code, modifier_cd=concept_code_coding, inst_num = 0
            3) concept_cd = predicate, modifier_cd=concept_code_coding, inst_num = inst_num

    :param g: Graph containing facts
    :param root_concept: level 0 concept associated with this entry
    :param subject: subject
    :param predicate: predicate
    :param ofk: Observation fact key
    :param instance_num: Observation fact instance number if non-zero
    :param identifying_codes: Observation fact root codes if inside an instance
    :return: Observation fact(s) if any that augment the basic subject/predicate
    """
    from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact   # Imported here to prevent recursive imports

    rval: List[ObservationFact] = []

    # Find any codeable concepts in the range of predicate
    for target in g.objects(subject, predicate):                        # Indirectly looking for FHIR:CodedEntry
        for target_p, target_o in g.predicate_objects(target):
            if target_p == FHIR.CodeableConcept.coding:                 # And interior FHIR:Coding
                target_concept_code = concept_uri_for(g, target_o)      # Look for type arc or synthesize it
                # Code must exist and we have to have a known namespace to proceed
                if target_concept_code and FHIRObservationFact.ns_name_for(target_concept_code):
                    if predicate in bare_codes:
                        # Predicate can serve as a concept_cd for the resource itself
                        # Add the root element and its values
                        rval += add_concept_values(g,
                                                   FHIRObservationFact(g, ofk, target_concept_code, None, None),
                                                   predicate,
                                                   subject)
                    if instance_num is None:
                        # Add an entry as a concept/modifier entry
                        rval += add_concept_values(g,
                                                   FHIRObservationFact(g, ofk, predicate, target_concept_code, None),
                                                   predicate,
                                                   subject)

                    else:
                        # Inner coded element -- create a set of base entries
                        base_entries = add_concept_values(
                            g,
                            FHIRObservationFact(g, ofk, root_concept, target_concept_code, None, instance_num),
                            predicate,
                            subject)
                        rval += base_entries
                        for id_code in identifying_codes:
                            # TODO: Kludge - id_code is in ns:name form and identifying codes are in URI form.  For the
                            # time being we are going to assume that the FHIR coding system will not be used for
                            # secondary identity.  Fix this
                            # if id_code not in bare_codes:
                            if not id_code.startswith("FHIR:"):
                                for entry in base_entries:
                                    fact_entry = copy.copy(entry)
                                    fact_entry._concept_cd = id_code
                                    fact_entry._modifier_cd = FHIRObservationFact.ns_name_for(target_concept_code)
                                    fact_entry._instance_num = 0
                                    rval.append(fact_entry)
                                if not base_entries:
                                    rval.append(FHIRObservationFact(g, ofk, id_code, target_concept_code, None))
            elif target_p == RDF.type and predicate not in (FHIR.CodeableConcept.coding, ):
                # For the moment, we assume that the only other type nodes are for ``code`` nodes
                # Code must exist and we have to have a known namespace to proceed
                if FHIRObservationFact.ns_name_for(target_o):
                    cvals = add_concept_values(g,
                                               FHIRObservationFact(g, ofk, predicate, target_o, None, None),
                                               predicate,
                                               subject)
                    cval = cvals[0]
                    cval._valtype_cd = valuetype_text
                    cval._tval_char = str(g.value(target, FHIR.value))
                    rval += cvals
    return rval


# List of concept codes that serve as identifier codes, meaning that they become standalone
# codes for the root node.
bare_codes: List[URIRef] = {
    FHIR.AdverseEvent.event,
    FHIR.AdverseEvent.seriousness,
    FHIR.AdverseEvent.severity,
    FHIR.AdverseEvent.outcome,

    # TODO: What to do about reaction[0..*] manifestation[1..*] entries? + exposure route
    FHIR.AllergyIntolerance.code,

    # CarePlan doesn't appear to have any primary elements.

    FHIR.Condition.code,

    FHIR.DiagnosticReport.code,

    FHIR.MedicationAdministration.medicationCodeableConcept,

    FHIR.MedicationDispense.medicationCodeableConcept,

    FHIR.MedicationRequest.medicationCodeableConcept,

    FHIR.MedicationStatement.medicationCodeableConcept,

    FHIR.NutritionOrder.oralDiet.type,
    FHIR.NutritionOrder.supplement.type,
    FHIR.NutritionOrder.enteralFormula.baseFormulaType,

    FHIR.Observation.code,
    FHIR.Observation.component.code,

    # TODO: We could consider folding eye into product where appropriate
    FHIR.VisionPrescription.dispense.product,           # Product that was dispensed
    FHIR.VisionPrescription.reasonCodeableConcept       # Indication for prescription
}

code_value_tuples: List[URIRef] = [
    FHIR.Observation.code,
    FHIR.Observation.component.code,
]
