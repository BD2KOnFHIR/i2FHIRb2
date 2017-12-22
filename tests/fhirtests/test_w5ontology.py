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
import os
import unittest

from rdflib import Graph
from tests.utils.base_test_case import test_data_directory, mvdir


class W5TestCase(unittest.TestCase):

    def test_w5_concepts(self):
        from i2fhirb2.fhir.fhirw5ontology import FHIRW5Ontology
        g = Graph()
        g.load(os.path.join(test_data_directory, 'fhir_metadata_vocabulary', 'w5.ttl'), format="turtle")
        self.assertEqual([
             'http://hl7.org/fhir/w5#administrative',
             'http://hl7.org/fhir/w5#administrative.device',
             'http://hl7.org/fhir/w5#administrative.entity',
             'http://hl7.org/fhir/w5#administrative.group',
             'http://hl7.org/fhir/w5#administrative.individual',
             'http://hl7.org/fhir/w5#clinical',
             'http://hl7.org/fhir/w5#clinical.careprovision',
             'http://hl7.org/fhir/w5#clinical.diagnostics',
             'http://hl7.org/fhir/w5#clinical.general',
             'http://hl7.org/fhir/w5#clinical.medication',
             'http://hl7.org/fhir/w5#financial',
             'http://hl7.org/fhir/w5#financial.billing',
             'http://hl7.org/fhir/w5#financial.other',
             'http://hl7.org/fhir/w5#financial.payment',
             'http://hl7.org/fhir/w5#financial.support',
             'http://hl7.org/fhir/w5#workflow',
             'http://hl7.org/fhir/w5#workflow.encounter',
             'http://hl7.org/fhir/w5#workflow.order',
             'http://hl7.org/fhir/w5#workflow.scheduling'],
            [str(e) for e in sorted(FHIRW5Ontology(g)._w5_concepts())])

    def test_w5_paths(self):
        from i2fhirb2.fhir.fhirw5ontology import FHIRW5Ontology
        g = Graph()
        g.load(os.path.join(test_data_directory, 'fhir_metadata_vocabulary', 'w5.ttl'), format="turtle")
        fot = FHIRW5Ontology(g)
        self.assertEqual([
             '\\FHIR\\administrative\\',
             '\\FHIR\\administrative\\device\\',
             '\\FHIR\\administrative\\entity\\',
             '\\FHIR\\administrative\\group\\',
             '\\FHIR\\administrative\\individual\\',
             '\\FHIR\\clinical\\',
             '\\FHIR\\clinical\\careprovision\\',
             '\\FHIR\\clinical\\diagnostics\\',
             '\\FHIR\\clinical\\general\\',
             '\\FHIR\\clinical\\medication\\',
             '\\FHIR\\financial\\',
             '\\FHIR\\financial\\billing\\',
             '\\FHIR\\financial\\other\\',
             '\\FHIR\\financial\\payment\\',
             '\\FHIR\\financial\\support\\',
             '\\FHIR\\workflow\\',
             '\\FHIR\\workflow\\encounter\\',
             '\\FHIR\\workflow\\order\\',
             '\\FHIR\\workflow\\scheduling\\'], [str(e) for e in sorted(fot.w5_paths())])

    def test_full_w5_paths(self):
        from i2fhirb2.fhir.fhirmetadatavocabulary import FHIRMetaDataVocabulary
        self.fmv = FHIRMetaDataVocabulary(os.path.join(mvdir, 'fhir.ttl'), os.path.join(mvdir, 'w5.ttl'))

        self.assertEqual([
           '\\FHIR\\administrative\\',
           '\\FHIR\\administrative\\device\\',
           '\\FHIR\\administrative\\device\\DeviceComponent\\:(http://hl7.org/fhir/DeviceComponent)',
           '\\FHIR\\administrative\\device\\DeviceMetric\\:(http://hl7.org/fhir/DeviceMetric)',
           '\\FHIR\\administrative\\device\\Device\\:(http://hl7.org/fhir/Device)',
           '\\FHIR\\administrative\\entity\\',
           '\\FHIR\\administrative\\entity\\Location\\:(http://hl7.org/fhir/Location)',
           '\\FHIR\\administrative\\entity\\Person\\:(http://hl7.org/fhir/Person)',
           '\\FHIR\\administrative\\entity\\ProductPlan\\:(http://hl7.org/fhir/ProductPlan)',
           '\\FHIR\\administrative\\entity\\Substance\\:(http://hl7.org/fhir/Substance)',
           '\\FHIR\\administrative\\group\\',
           '\\FHIR\\administrative\\group\\Group\\:(http://hl7.org/fhir/Group)',
           '\\FHIR\\administrative\\group\\HealthcareService\\:(http://hl7.org/fhir/HealthcareService)',
           '\\FHIR\\administrative\\group\\Organization\\:(http://hl7.org/fhir/Organization)',
           '\\FHIR\\administrative\\individual\\',
           '\\FHIR\\administrative\\individual\\OrganizationRole\\:(http://hl7.org/fhir/OrganizationRole)',
           '\\FHIR\\administrative\\individual\\Patient\\:(http://hl7.org/fhir/Patient)',
           '\\FHIR\\administrative\\individual\\PractitionerRole\\:(http://hl7.org/fhir/PractitionerRole)',
           '\\FHIR\\administrative\\individual\\Practitioner\\:(http://hl7.org/fhir/Practitioner)',
           '\\FHIR\\administrative\\individual\\RelatedPerson\\:(http://hl7.org/fhir/RelatedPerson)',
           '\\FHIR\\clinical\\',
           '\\FHIR\\clinical\\careprovision\\',
           '\\FHIR\\clinical\\careprovision\\CarePlan\\:(http://hl7.org/fhir/CarePlan)',
           '\\FHIR\\clinical\\careprovision\\CareTeam\\:(http://hl7.org/fhir/CareTeam)',
           '\\FHIR\\clinical\\careprovision\\Goal\\:(http://hl7.org/fhir/Goal)',
           '\\FHIR\\clinical\\careprovision\\NutritionOrder\\:(http://hl7.org/fhir/NutritionOrder)',
           '\\FHIR\\clinical\\careprovision\\VisionPrescription\\:(http://hl7.org/fhir/VisionPrescription)',
           '\\FHIR\\clinical\\diagnostics\\',
           '\\FHIR\\clinical\\diagnostics\\BodyStructure\\:(http://hl7.org/fhir/BodyStructure)',
           '\\FHIR\\clinical\\diagnostics\\DiagnosticReport\\:(http://hl7.org/fhir/DiagnosticReport)',
           '\\FHIR\\clinical\\diagnostics\\ImagingStudy\\:(http://hl7.org/fhir/ImagingStudy)',
           '\\FHIR\\clinical\\diagnostics\\ObservationDefinition\\:(http://hl7.org/fhir/ObservationDefinition)',
           '\\FHIR\\clinical\\diagnostics\\Observation\\:(http://hl7.org/fhir/Observation)',
           '\\FHIR\\clinical\\diagnostics\\ResearchStudy\\:(http://hl7.org/fhir/ResearchStudy)',
           '\\FHIR\\clinical\\diagnostics\\ResearchSubject\\:(http://hl7.org/fhir/ResearchSubject)',
           '\\FHIR\\clinical\\diagnostics\\Sequence\\:(http://hl7.org/fhir/Sequence)',
           '\\FHIR\\clinical\\diagnostics\\SpecimenDefinition\\:(http://hl7.org/fhir/SpecimenDefinition)',
           '\\FHIR\\clinical\\diagnostics\\Specimen\\:(http://hl7.org/fhir/Specimen)',
           '\\FHIR\\clinical\\general\\',
           '\\FHIR\\clinical\\general\\ActivityDefinition\\:(http://hl7.org/fhir/ActivityDefinition)',
           '\\FHIR\\clinical\\general\\AdverseEvent\\:(http://hl7.org/fhir/AdverseEvent)',
           '\\FHIR\\clinical\\general\\AllergyIntolerance\\:(http://hl7.org/fhir/AllergyIntolerance)',
           '\\FHIR\\clinical\\general\\ClinicalImpression\\:(http://hl7.org/fhir/ClinicalImpression)',
           '\\FHIR\\clinical\\general\\Condition\\:(http://hl7.org/fhir/Condition)',
           '\\FHIR\\clinical\\general\\DetectedIssue\\:(http://hl7.org/fhir/DetectedIssue)',
           '\\FHIR\\clinical\\general\\EventDefinition\\:(http://hl7.org/fhir/EventDefinition)',
           '\\FHIR\\clinical\\general\\FamilyMemberHistory\\:(http://hl7.org/fhir/FamilyMemberHistory)',
           '\\FHIR\\clinical\\general\\GuidanceResponse\\:(http://hl7.org/fhir/GuidanceResponse)',
           '\\FHIR\\clinical\\general\\Library\\:(http://hl7.org/fhir/Library)',
           '\\FHIR\\clinical\\general\\MeasureReport\\:(http://hl7.org/fhir/MeasureReport)',
           '\\FHIR\\clinical\\general\\Measure\\:(http://hl7.org/fhir/Measure)',
           '\\FHIR\\clinical\\general\\PlanDefinition\\:(http://hl7.org/fhir/PlanDefinition)',
           '\\FHIR\\clinical\\general\\Procedure\\:(http://hl7.org/fhir/Procedure)',
           '\\FHIR\\clinical\\general\\RequestGroup\\:(http://hl7.org/fhir/RequestGroup)',
           '\\FHIR\\clinical\\general\\RiskAssessment\\:(http://hl7.org/fhir/RiskAssessment)',
           '\\FHIR\\clinical\\general\\ServiceDefinition\\:(http://hl7.org/fhir/ServiceDefinition)',
           '\\FHIR\\clinical\\general\\ServiceRequest\\:(http://hl7.org/fhir/ServiceRequest)',
           '\\FHIR\\clinical\\general\\UserSession\\:(http://hl7.org/fhir/UserSession)',
           '\\FHIR\\clinical\\medication\\',
           '\\FHIR\\clinical\\medication\\ImmunizationEvaluation\\:(http://hl7.org/fhir/ImmunizationEvaluation)',
           '\\FHIR\\clinical\\medication\\ImmunizationRecommendation\\:'
           '(http://hl7.org/fhir/ImmunizationRecommendation)',
           '\\FHIR\\clinical\\medication\\Immunization\\:(http://hl7.org/fhir/Immunization)',
           '\\FHIR\\clinical\\medication\\MedicationAdministration\\:(http://hl7.org/fhir/MedicationAdministration)',
           '\\FHIR\\clinical\\medication\\MedicationDispense\\:(http://hl7.org/fhir/MedicationDispense)',
           '\\FHIR\\clinical\\medication\\MedicationRequest\\:(http://hl7.org/fhir/MedicationRequest)',
           '\\FHIR\\clinical\\medication\\MedicationStatement\\:(http://hl7.org/fhir/MedicationStatement)',
           '\\FHIR\\clinical\\medication\\Medication\\:(http://hl7.org/fhir/Medication)',
           '\\FHIR\\financial\\',
           '\\FHIR\\financial\\billing\\',
           '\\FHIR\\financial\\billing\\ClaimResponse\\:(http://hl7.org/fhir/ClaimResponse)',
           '\\FHIR\\financial\\billing\\Claim\\:(http://hl7.org/fhir/Claim)',
           '\\FHIR\\financial\\other\\',
           '\\FHIR\\financial\\other\\Contract\\:(http://hl7.org/fhir/Contract)',
           '\\FHIR\\financial\\other\\ExplanationOfBenefit\\:(http://hl7.org/fhir/ExplanationOfBenefit)',
           '\\FHIR\\financial\\payment\\',
           '\\FHIR\\financial\\payment\\PaymentNotice\\:(http://hl7.org/fhir/PaymentNotice)',
           '\\FHIR\\financial\\payment\\PaymentReconciliation\\:(http://hl7.org/fhir/PaymentReconciliation)',
           '\\FHIR\\financial\\support\\',
           '\\FHIR\\financial\\support\\Account\\:(http://hl7.org/fhir/Account)',
           '\\FHIR\\financial\\support\\ChargeItem\\:(http://hl7.org/fhir/ChargeItem)',
           '\\FHIR\\financial\\support\\Coverage\\:(http://hl7.org/fhir/Coverage)',
           '\\FHIR\\financial\\support\\EligibilityRequest\\:(http://hl7.org/fhir/EligibilityRequest)',
           '\\FHIR\\financial\\support\\EligibilityResponse\\:(http://hl7.org/fhir/EligibilityResponse)',
           '\\FHIR\\financial\\support\\EnrollmentRequest\\:(http://hl7.org/fhir/EnrollmentRequest)',
           '\\FHIR\\financial\\support\\EnrollmentResponse\\:(http://hl7.org/fhir/EnrollmentResponse)',
           '\\FHIR\\financial\\support\\Invoice\\:(http://hl7.org/fhir/Invoice)',
           '\\FHIR\\workflow\\',
           '\\FHIR\\workflow\\encounter\\',
           '\\FHIR\\workflow\\encounter\\Communication\\:(http://hl7.org/fhir/Communication)',
           '\\FHIR\\workflow\\encounter\\Encounter\\:(http://hl7.org/fhir/Encounter)',
           '\\FHIR\\workflow\\encounter\\EpisodeOfCare\\:(http://hl7.org/fhir/EpisodeOfCare)',
           '\\FHIR\\workflow\\encounter\\Flag\\:(http://hl7.org/fhir/Flag)',
           '\\FHIR\\workflow\\order\\',
           '\\FHIR\\workflow\\order\\CommunicationRequest\\:(http://hl7.org/fhir/CommunicationRequest)',
           '\\FHIR\\workflow\\order\\DeviceRequest\\:(http://hl7.org/fhir/DeviceRequest)',
           '\\FHIR\\workflow\\order\\DeviceUseStatement\\:(http://hl7.org/fhir/DeviceUseStatement)',
           '\\FHIR\\workflow\\order\\ProcessRequest\\:(http://hl7.org/fhir/ProcessRequest)',
           '\\FHIR\\workflow\\order\\ProcessResponse\\:(http://hl7.org/fhir/ProcessResponse)',
           '\\FHIR\\workflow\\order\\SupplyDelivery\\:(http://hl7.org/fhir/SupplyDelivery)',
           '\\FHIR\\workflow\\order\\SupplyRequest\\:(http://hl7.org/fhir/SupplyRequest)',
           '\\FHIR\\workflow\\order\\Task\\:(http://hl7.org/fhir/Task)',
           '\\FHIR\\workflow\\scheduling\\',
           '\\FHIR\\workflow\\scheduling\\AppointmentResponse\\:(http://hl7.org/fhir/AppointmentResponse)',
           '\\FHIR\\workflow\\scheduling\\Appointment\\:(http://hl7.org/fhir/Appointment)',
           '\\FHIR\\workflow\\scheduling\\Schedule\\:(http://hl7.org/fhir/Schedule)',
           '\\FHIR\\workflow\\scheduling\\Slot\\:(http://hl7.org/fhir/Slot)'],
            [str(e) for e in sorted(self.fmv.w5_graph.w5_paths())])


if __name__ == '__main__':
    unittest.main()
