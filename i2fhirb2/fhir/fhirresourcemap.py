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
from typing import Optional, Dict, Tuple

from rdflib import URIRef, Graph, RDF

from i2fhirb2.fhir.fhirspecific import FHIR, FHIR_RESOURCE_RE
from i2fhirb2.rdfsupport.fhirgraphutils import value, link


class FHIR_Resource_type:
    pass


class FHIR_Infrastructure_type(FHIR_Resource_type):
    pass


class FHIR_Observation_type(FHIR_Resource_type):
    def __init__(self, patient_ref: URIRef, encounter_ref: Optional[URIRef], provider_ref: Optional[URIRef]):
        self.patient_ref = patient_ref
        self.encounter_ref = encounter_ref
        self.provider_ref = provider_ref

    def fact_key_for(self, g: Graph, subj: URIRef) -> Tuple[Optional[URIRef], Optional[URIRef], Optional[URIRef]]:
        pat_uri, pat_type = link(g, subj, self.patient_ref)
        if pat_type and pat_type != FHIR.Patient:
            return None, None, None
        if self.encounter_ref:
            encounter_uri, encounter_type = link(g, subj, self.encounter_ref)
            # TODO: Figure out what types of things count here
        else:
            encounter_uri = None
        if self.provider_ref:
            provider_uri, provider_type = link(g, subj, self.provider_ref)
            # TODO: Figure out what counts as a provider
            # if provider_type not in {FHIR.Organization}:
            #   provider_uri = None
        else:
            provider_uri = None
        return pat_uri, encounter_uri, provider_uri


class FHIR_Visit_Dimension_type(FHIR_Resource_type):
    def __init__(self, patient_ref: str):
        self.patient_ref = patient_ref


class FHIR_Provider_Dimension_type(FHIR_Resource_type):
    pass


class FHIR_Patient_Dimension_type(FHIR_Resource_type):
    pass


class FHIR_Bundle_type(FHIR_Resource_type):
    pass


FHIR_RESOURCE_MAP: Dict[URIRef, Optional[FHIR_Resource_type]] = {
    FHIR.Account: FHIR_Observation_type(FHIR.Account.subject, None, FHIR.Account.owner),
    FHIR.ActivityDefinition: None,
    FHIR.AdverseEvent: None,
    FHIR.AllergyIntolerance: None,
    FHIR.Appointment: None,
    FHIR.AppointmentResponse: None,
    FHIR.AuditEvent: None,
    FHIR.Basic: None,
    FHIR.Binary: None,
    FHIR.BodyStructure: None,
    FHIR.Bundle: FHIR_Bundle_type,
    FHIR.CapabilityStatement: None,
    FHIR.CarePlan: FHIR_Observation_type(FHIR.CarePlan.subject, FHIR.CarePlan.context, None),
    FHIR.CareTeam: None,
    FHIR.ChargeItem: None,
    FHIR.Claim: None,
    FHIR.ClaimResponse: None,
    FHIR.ClinicalImpression: None,
    FHIR.CodeSystem: None,
    FHIR.Communication: None,
    FHIR.CommunicationRequest: None,
    FHIR.CompartmentDefinition: None,
    FHIR.Composition: None,
    FHIR.ConceptMap: None,
    FHIR.Condition: FHIR_Observation_type(FHIR.Condition.subject, FHIR.Condition.context, FHIR.Condition.asserter),
    FHIR.Consent: None,
    FHIR.Contract: None,
    FHIR.Coverage: None,
    FHIR.DetectedIssue: None,
    FHIR.Device: None,
    FHIR.DeviceComponent: None,
    FHIR.DeviceMetric: None,
    FHIR.DeviceRequest: None,
    FHIR.DeviceUseStatement: None,
    FHIR.DiagnosticReport: FHIR_Observation_type(FHIR.DiagnosticReport.subject, FHIR.DiagnosticReport.context,
                                                 FHIR.DiagnosticReport.performer),
    FHIR.DocumentManifest: None,
    FHIR.DocumentReference: None,
    FHIR.EligibilityRequest: None,
    FHIR.EligibilityResponse: None,
    FHIR.Encounter: FHIR_Visit_Dimension_type(FHIR.Encounter.subject),
    FHIR.Endpoint: None,
    FHIR.EnrollmentRequest: None,
    FHIR.EnrollmentResponse: None,
    FHIR.EpisodeOfCare: None,
    FHIR.EventDefinition: None,
    FHIR.ExpansionProfile: None,
    FHIR.ExplanationOfBenefit: None,
    FHIR.FamilyMemberHistory: None,
    FHIR.Flag: None,
    FHIR.Goal: None,
    FHIR.GraphDefinition: None,
    FHIR.Group: None,
    FHIR.GuidanceResponse: None,
    FHIR.HealthcareService: None,
    FHIR.ImagingManifest: None,
    FHIR.ImagingStudy: None,
    FHIR.Immunization: None,
    FHIR.ImmunizationRecommendation: None,
    FHIR.ImplementationGuide: None,
    FHIR.Library: None,
    FHIR.Linkage: None,
    FHIR.List: None,
    FHIR.Location: None,
    FHIR.Measure: None,
    FHIR.MeasureReport: None,
    FHIR.Media: None,
    FHIR.Medication: None,
    FHIR.MedicationAdministration: None,
    FHIR.MedicationDispense: None,
    FHIR.MedicationRequest: FHIR_Observation_type(FHIR.MedicationRequest.subject, FHIR.MedicationRequest.context,
                                                  FHIR.MedicationRequest.requester),
    FHIR.MedicationStatement: None,
    FHIR.MessageDefinition: None,
    FHIR.MessageHeader: None,
    FHIR.NamingSystem: None,
    FHIR.NutritionOrder: None,
    FHIR.Observation: FHIR_Observation_type(FHIR.Observation.subject, FHIR.Observation.context,
                                            FHIR.Observation.performer),
    FHIR.OperationDefinition: None,
    FHIR.OperationOutcome: None,
    FHIR.Organization: FHIR_Provider_Dimension_type(),
    FHIR.Patient: FHIR_Patient_Dimension_type(),
    FHIR.PaymentNotice: None,
    FHIR.PaymentReconciliation: None,
    FHIR.Person: None,
    FHIR.PlanDefinition: None,
    FHIR.Practitioner: None,
    FHIR.PractitionerRole: None,
    FHIR.Procedure: None,
    FHIR.ProcedureRequest: None,
    FHIR.ProcessRequest: None,
    FHIR.ProcessResponse: None,
    FHIR.Provenance: None,
    FHIR.Questionnaire: None,
    FHIR.QuestionnaireResponse: None,
    FHIR.RelatedPerson: None,
    FHIR.RequestGroup: None,
    FHIR.ResearchStudy: None,
    FHIR.ResearchSubject: None,
    FHIR.RiskAssessment: None,
    FHIR.Schedule: None,
    FHIR.SearchParameter: None,
    FHIR.Sequence: None,
    FHIR.ServiceDefinition: None,
    FHIR.Slot: None,
    FHIR.Specimen: None,
    FHIR.StructureDefinition: None,
    FHIR.StructureMap: None,
    FHIR.Subscription: None,
    FHIR.Substance: None,
    FHIR.SupplyDelivery: None,
    FHIR.SupplyRequest: None,
    FHIR.Task: None,
    FHIR.TestReport: FHIR_Infrastructure_type,
    FHIR.TestScript: FHIR_Infrastructure_type,
    FHIR.ValueSet: FHIR_Infrastructure_type(),
    FHIR.VisionPrescription: FHIR_Observation_type(FHIR.VisionPrescription.patient, FHIR.VisionPrescription.encounter,
                                                   FHIR.VisionPrescription.prescriber)
}