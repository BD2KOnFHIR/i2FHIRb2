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

import os

import re
import unittest
from contextlib import redirect_stdout, contextmanager
from functools import total_ordering
from io import StringIO
from typing import List, Optional

from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact
from i2b2model.data.i2b2observationfact import ObservationFact
from tests.utils.fhir_graph import test_data_directory
from tests.utils.load_facts_helper import LoadFactsHelper
from dynprops import clear, row


@total_ordering
class ObsElement:
    """ Salient elements in an Observation Fact entry """
    def __init__(self, concept_cd: str, modifier_cd: str="@", instance_num: int=0, tval_char: Optional[str]=None,
                 nval_num: Optional[float]=None, encounter_num: int=0, units_cd: Optional[str]=None,
                 alternate_tvals: List[str]=None) -> None:
        self.instance_num = instance_num
        self.concept_cd = concept_cd
        self.modifier_cd = modifier_cd
        self.tval_char = tval_char
        self.nval_num = nval_num
        self.units_cd = units_cd
        self.encounter_num = encounter_num  # 0 means no encounter number
        self.alternate_tvals = [tval_char] + (alternate_tvals if alternate_tvals else [])

    def __str__(self) -> str:
        return f"{self.instance_num}, {self.concept_cd}, {self.modifier_cd}, {self.tval_char}, {self.nval_num}, " \
               f"{self.units_cd}"

    def __repr__(self) -> str:
        rval = "ObsElement(" + f'"{self.concept_cd}"'
        if self.modifier_cd != '@' or self.instance_num:
            rval += f', "{self.modifier_cd}"'
        if self.instance_num:
            rval += f', {self.instance_num}'
        if self.tval_char:
            rval += f', tval_char="{self.tval_char}"'
        if self.nval_num is not None:
            rval += f', nval_num={self.nval_num}'
        if self.units_cd:
            rval += f', units_cd="{self.units_cd}"'
        return rval + ')'

    def __eq__(self, other: "ObsElement") -> bool:
        if not isinstance(other, ObsElement):
            return NotImplemented
        if not ((self.encounter_num == 0 or other.encounter_num == 0 or self.encounter_num == other.encounter_num) and
                self.instance_num == other.instance_num and self.concept_cd == other.concept_cd and
                self.nval_num == other.nval_num and self.units_cd == other.units_cd):
            return False
        return any(tval_char in other.alternate_tvals for tval_char in self.alternate_tvals)

    def __lt__(self, other: "ObsElement") -> bool:
        if not isinstance(other, ObsElement):
            return NotImplemented
        return self.encounter_num < other.encounter_num or \
            (self.encounter_num == other.encounter_num and str(self) < str(other))


def obs_element(fact: ObservationFact) -> ObsElement:
    """ Construct an ObsElement from an observation fact

    :param fact:
    :return:
    """
    return ObsElement(fact.concept_cd, fact.modifier_cd, fact.instance_num, fact.tval_char, fact.nval_num,
                      fact.encounter_num, fact.units_cd)


# Considered an error if any of these appear in the output
not_expected_in_output = [r'Unrecognized namespace: .*', r'Collision: .*', r'.*Modifier on modifier']


class CodeMappingResourcesTestCase(LoadFactsHelper):
    caller_filename = __file__
    data_source = 'http://build.fhir.org/'
    print_output = False            # Print the output log
    summarize_output = False         # Print the results
    print_output_filter = ""        # Results filter

    @staticmethod
    def _has_entry(ofl: List[ObservationFact],  entry: ObsElement) -> bool:
        return any(obs_element(fact) == entry for fact in ofl)

    @contextmanager
    def synthea_test(self) -> None:
        """ Run the test against the synthea_data/ttl test directory instead of the default

        """
        old_data_source = self.data_source
        self.data_source = os.path.join(test_data_directory, 'synthea_data', 'ttl')
        try:
            yield
        finally:
            self.data_source = old_data_source

    @contextmanager
    def fhir_core(self) -> None:
        """ Run the test against the data/fhir_core_ttl directory rather than the default

        """
        old_data_source = self.data_source
        self.data_source = os.path.join(test_data_directory, 'fhir_core_ttl')
        try:
            yield
        finally:
            self.data_source = old_data_source

    def run_test(self, fname: str, expected_facts: List[ObsElement], unexpected_facts: List[ObsElement] = None,
                 expected_in_output: Optional[List[str]]=()) -> None:
        clear(FHIRObservationFact)
        output_buffer = StringIO()
        with redirect_stdout(output_buffer):
            ofl = self.load_i2b2_to_memory(fname, self.data_source)
        if self.print_output:
            print(output_buffer.getvalue())
        if self.summarize_output:
            print("*" * 20)
            print(',\n'.join([repr(e) for e in sorted([obs_element(e) for e in ofl.observation_facts
                                                      if e.concept_cd.startswith(self.print_output_filter)])]))

        output = output_buffer.getvalue()

        # Check for expected output
        for expected_output in expected_in_output:
            if not re.search(expected_output, output, flags=re.MULTILINE):
                self.assertTrue(False, f"Expected to find {expected_output}")

        # Check for unexpected output
        for not_expected in not_expected_in_output:
            m = re.search(not_expected, output, flags=re.MULTILINE)
            if m and not any(re.search(expected_output, m.group(0)) for expected_output in expected_in_output):
                self.assertTrue(False, f'Unexpected output: "{m.group(0)}"')

        # Check for expected facts
        for expected_fact in expected_facts:
            self.assertTrue(self._has_entry(ofl.observation_facts, expected_fact), f"Missing entry: {expected_fact}")

        # Make sure unexpected facts aren't there
        for unexpected_fact in unexpected_facts if unexpected_facts is not None else []:
            self.assertFalse(self._has_entry(ofl.observation_facts, unexpected_fact),
                             f"Should not be emitted: {unexpected_fact}")

    def test_adverse_event(self):
        """ Test adverseevent-example.ttl """
        # TODO: causality assessment and method are untested
        self.run_test('adverseevent-example.ttl', [
            ObsElement("FHIR:AdverseEvent.category", "ADVERSE-EVENT-CATEGORY:ProductUseError"),
            ObsElement("ADVERSE-EVENT-SERIOUSNESS:Non-serious"),
            ObsElement("ADVERSE-EVENT-SEVERITY:Mild"),
            ObsElement("SCT:304386008"),
            ObsElement("FHIR:AdverseEvent")])

    def test_allergy_intolerance_1(self):
        with self.fhir_core():
            self.run_test('allergyintolerance-medication.ttl',
                          [ObsElement("RXNORM:7980"),
                           ObsElement("FHIR:AllergyIntolerance"),
                           ObsElement("FHIR:AllergyIntolerance.category", "ALLERGY-INTOLERANCE-CATEGORY:medication",
                                      tval_char="medication"),
                           ObsElement("FHIR:AllergyIntolerance.clinicalStatus", "ALLERGY-CLINICAL-STATUS:active",
                                      tval_char="active"),
                           ObsElement("FHIR:AllergyIntolerance.criticality", "ALLERGY-INTOLERANCE-CRITICALITY:high",
                                      tval_char="high"),
                           ObsElement("FHIR:AllergyIntolerance.reaction", "SCT:247472004", 1)],
                          [ObsElement("RXNORM:7987", "SCT:247472004"),
                           ObsElement("SCT:247472004")])

    def test_allergy_intolerance_2(self):
        """ Test Schaefer199_Vivienne674_19.ttl """
        with self.synthea_test():
            self.run_test('Schaefer199_Vivienne674_19.ttl', [])

    def test_care_plan(self):
        """ Test careplan-example-integrated.ttl """
        self.run_test('careplan-example-integrated.ttl',
                      [ObsElement("FHIR:CarePlan")])

    def test_care_plan_2(self):
        """ Test Roob122_Jennie897_53.ttl """
        with self.synthea_test():
            self.run_test('Roob122_Jennie897_53.ttl',
                          [
                            ObsElement("FHIR:CarePlan.category", "SCT:326051000000105", 0),
                            ObsElement("FHIR:CarePlan.activity", "SCT:58332002", 1),
                            ObsElement("FHIR:CarePlan.category", "SCT:869761000000107", 0),
                            ObsElement("FHIR:CarePlan.activity", "SCT:223472008", 1),
                            ObsElement("FHIR:CarePlan.activity", "SCT:171245007", 2),
                            ObsElement("FHIR:CarePlan.category", "SCT:326051000000105", 0),
                            ObsElement("FHIR:CarePlan.activity", "SCT:58332002", 1),
                            ObsElement("FHIR:CarePlan.activity", "SCT:409002", 2),
                            ObsElement("FHIR:CarePlan.category", "SCT:869761000000107", 0),
                            ObsElement("FHIR:CarePlan.activity", "SCT:223472008", 1),
                            ObsElement("FHIR:CarePlan.activity", "SCT:171245007", 2)])

    def test_condition(self):
        """ Test: condition-example-f002-lung.ttl """
        self.run_test('condition-example-f002-lung.ttl',
                      [
                          ObsElement("SCT:254637007"),
                          ObsElement("SCT:254637007", "SCT:169069000"),
                          ObsElement("FHIR:Condition.bodySite", "SCT:51185008"),
                          ObsElement("FHIR:Condition.category", "SCT:439401001"),
                          ObsElement("FHIR:Condition.code", "SCT:254637007"),
                          ObsElement("FHIR:Condition.evidence", "SCT:169069000", 3),
                          ObsElement("FHIR:Condition.severity", "SCT:24484000"),
                          ObsElement("FHIR:Condition.stage", "SCT:258219007", 4),
                          ObsElement("FHIR:Condition.stage", "SCT:260998006", 4)
                      ])

    def test_observation(self):
        """ Test: observation-example-glasgow.ttl """
        with self.fhir_core():
            self.run_test('observation-example-glasgow.ttl',
                          [ObsElement("FHIR:Observation.status", "OBSERVATION-STATUS:final", tval_char='final'),
                           ObsElement("FHIR:Observation"),
                           ObsElement("FHIR:Observation.code", "LOINC:9269-2", tval_char="E", nval_num=13,
                                      units_cd="{score}"),
                           ObsElement("LOINC:9267-6", tval_char="Opens eyes spontaneously"),
                           ObsElement("LOINC:9267-6", "LOINC:LA6556-0", tval_char="Eyes open spontaneously"),
                           ObsElement("LOINC:9268-4", tval_char="Localizes painful stimuli (acme)"),
                           ObsElement("LOINC:9268-4", "LOINC:LA6566-9", tval_char="Localizing pain"),
                           ObsElement("LOINC:9269-2", tval_char="E", nval_num=13, units_cd="{score}"),
                           ObsElement("LOINC:9269-2", "LOINC:9267-6", tval_char="Opens eyes spontaneously"),
                           ObsElement("LOINC:9269-2", "LOINC:9268-4", tval_char="Localizes painful stimuli (acme)"),
                           ObsElement("LOINC:9269-2", "LOINC:9270-0", tval_char="Confused, disoriented"),
                           ObsElement("LOINC:9269-2", "LOINC:LA6556-0", tval_char="Opens eyes spontaneously"),
                           ObsElement("LOINC:9269-2", "LOINC:LA6560-2", tval_char="Confused, disoriented"),
                           ObsElement("LOINC:9269-2", "LOINC:LA6566-9", tval_char="Localizes painful stimuli (acme)"),
                           ObsElement("LOINC:9270-0", tval_char="Confused, disoriented"),
                           ObsElement("LOINC:9270-0", "LOINC:LA6560-2", tval_char="Confused"),
                           ObsElement("FHIR:Observation.component", "LOINC:9270-0", 1,
                                      tval_char="Confused, disoriented"),
                           ObsElement("FHIR:Observation.component", "LOINC:LA6560-2", 1,
                                      tval_char="Confused, disoriented"),
                           ObsElement("FHIR:Observation.component", "LOINC:9267-6", 2,
                                      tval_char="Opens eyes spontaneously"),
                           ObsElement("FHIR:Observation.component", "LOINC:LA6556-0", 2,
                                      tval_char="Opens eyes spontaneously"),
                           ObsElement("FHIR:Observation.component", "LOINC:9268-4", 3,
                                      tval_char="Localizes painful stimuli (acme)"),
                           ObsElement("FHIR:Observation.component", "LOINC:LA6566-9", 3,
                                      tval_char="Localizes painful stimuli (acme)")
                           ], [],
                          [
                                'Unrecognized namespace: http:/acme.ec/codes/',
                                'FHIR:Observation.component, LOINC:9270-0: Modifier on modifier',
                                'FHIR:Observation.component, LOINC:LA6560-2: Modifier on modifier',
                                'FHIR:Observation.component, LOINC:9267-6: Modifier on modifier',
                                'FHIR:Observation.component, LOINC:LA6556-0: Modifier on modifier',
                                'FHIR:Observation.component, LOINC:9268-4: Modifier on modifier',
                                'FHIR:Observation.component, LOINC:LA6566-9: Modifier on modifier',
                          ])

    def test_observation_2(self):
        """ Test observation-example-glasgow-short.ttl"""
        with self.fhir_core():
            self.run_test('observation-example-glasgow-short.ttl',
                          [ObsElement("FHIR:Observation.status", "OBSERVATION-STATUS:final", tval_char='final'),
                           # Observation code/value
                           ObsElement("LOINC:9269-2", tval_char="E", nval_num=13, units_cd="{score}"),
                           # Observation component 0, value 0
                           ObsElement("LOINC:9268-4", tval_char="Localizes painful stimuli (acme)",
                                      alternate_tvals=["Localizing pain", "5 (Localizes painful stimuli)"]),
                           ObsElement("LOINC:9269-2", "LOINC:9268-4", tval_char="Localizes painful stimuli (acme)",
                                      alternate_tvals=["Localizing pain", "5 (Localizes painful stimuli)"]),
                           # Observation component 0, value 1
                           ObsElement("LOINC:9268-4", "LOINC:LA6566-9", tval_char="Localizing pain"),
                           # text
                           ],

                          [ObsElement("FHIR:Observation.status", "OBSERVATION-STATUS:final"),
                           ObsElement("FHIR:CodeableConcept.coding", "LOINC:9267-6"),
                           ObsElement("LOINC:LA6566-9", "LOINC:LA6566-9", tval_char="5 (Localizes painful stimuli)")],
                          [r'Unrecognized namespace: http:/acme.ec/codes/',
                           r'FHIR:Observation.component, LOINC:9268-4: Modifier on modifier'])

    def test_visionprescription(self):
        """ Test: visionprescription-example-1.ttl """
        with self.fhir_core():
            self.run_test('visionprescription-example-1.ttl',
                          [ObsElement("EX-VISIONPRESCRIPTIONPRODUCT:contact"),
                           ObsElement("FHIR:VisionPrescription.dispense", "EX-VISIONPRESCRIPTIONPRODUCT:contact", 1),
                           ObsElement("FHIR:VisionPrescription.dispense", "EX-VISIONPRESCRIPTIONPRODUCT:contact", 2),
                           ObsElement("FHIR:VisionPrescription")],
                          [], [r'Unrecognized namespace: http://samplevisionreasoncodes.com/'])


if __name__ == '__main__':
    unittest.main()
