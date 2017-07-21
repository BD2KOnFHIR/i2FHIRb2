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
from typing import Optional, Dict

from rdflib import URIRef

from i2fhirb2.fhir.fhirspecific import FHIR


class FHIR_Resource_type:
    pass


class FHIR_Infrastructure_type(FHIR_Resource_type):
    pass


class FHIR_Observation_type(FHIR_Resource_type):
    def __init__(self, patient_ref: str, encounter_ref: Optional[str], provider_ref: str):
        self.patient_ref = patient_ref
        self.encounter_ref = encounter_ref
        self.provider_ref = provider_ref


class FHIR_Visit_Dimension_type(FHIR_Resource_type):
    def __init__(self, patient_ref: str):
        self.patient_ref = patient_ref


class FHIR_Provider_Dimension_type(FHIR_Resource_type):
    pass


class FHIR_Patient_Dimension_type(FHIR_Resource_type):
    pass


FHIR_RESOURCE_MAP: Dict[str, Optional[FHIR_Resource_type]] = {
    "Account": FHIR_Observation_type("subject", None, "owner"),
    "ActivityDefinition": None,
    "AdverseEvent": None,
    "AllergyIntolerance": None,
    "Appointment": None,
    "AppointmentResponse": None,
    "AuditEvent": None,
    "Basic": None,
    "Binary": None,
    "BodyStructure": None,
    "Bundle": None,
    "CapabilityStatement": None,
    "CarePlan": FHIR_Observation_type("subject", "context", "performer"),
    "CareTeam": None,
    "ChargeItem": None,
    "Claim": None,
    "ClaimResponse": None,
    "ClinicalImpression": None,
    "CodeSystem": None,
    "Communication": None,
    "CommunicationRequest": None,
    "CompartmentDefinition": None,
    "Composition": None,
    "ConceptMap": None,
    "Condition": FHIR_Observation_type("subject", "context", "asserter"),
    "Consent": None,
    "Contract": None,
    "Coverage": None,
    "DetectedIssue": None,
    "Device": None,
    "DeviceComponent": None,
    "DeviceMetric": None,
    "DeviceRequest": None,
    "DeviceUseStatement": None,
    "DiagnosticReport": FHIR_Observation_type("subject", "context", "performer"),
    "DocumentManifest": None,
    "DocumentReference": None,
    "EligibilityRequest": None,
    "EligibilityResponse": None,
    "Encounter": FHIR_Visit_Dimension_type("subject"),
    "Endpoint": None,
    "EnrollmentRequest": None,
    "EnrollmentResponse": None,
    "EpisodeOfCare": None,
    "EventDefinition": None,
    "ExpansionProfile": None,
    "ExplanationOfBenefit": None,
    "FamilyMemberHistory": None,
    "Flag": None,
    "Goal": None,
    "GraphDefinition": None,
    "Group": None,
    "GuidanceResponse": None,
    "HealthcareService": None,
    "ImagingManifest": None,
    "ImagingStudy": None,
    "Immunization": None,
    "ImmunizationRecommendation": None,
    "ImplementationGuide": None,
    "Library": None,
    "Linkage": None,
    "List": None,
    "Location": None,
    "Measure": None,
    "MeasureReport": None,
    "Media": None,
    "Medication": None,
    "MedicationAdministration": None,
    "MedicationDispense": None,
    "MedicationRequest": FHIR_Observation_type("subject", "context", "requester"),
    "MedicationStatement": None,
    "MessageDefinition": None,
    "MessageHeader": None,
    "NamingSystem": None,
    "NutritionOrder": None,
    "Observation": FHIR_Observation_type("subject", "context", "performer"),
    "OperationDefinition": None,
    "OperationOutcome": None,
    "Organization": FHIR_Provider_Dimension_type(),
    "Patient": FHIR_Patient_Dimension_type(),
    "PaymentNotice": None,
    "PaymentReconciliation": None,
    "Person": None,
    "PlanDefinition": None,
    "Practitioner": None,
    "PractitionerRole": None,
    "Procedure": None,
    "ProcedureRequest": None,
    "ProcessRequest": None,
    "ProcessResponse": None,
    "Provenance": None,
    "Questionnaire": None,
    "QuestionnaireResponse": None,
    "RelatedPerson": None,
    "RequestGroup": None,
    "ResearchStudy": None,
    "ResearchSubject": None,
    "RiskAssessment": None,
    "Schedule": None,
    "SearchParameter": None,
    "Sequence": None,
    "ServiceDefinition": None,
    "Slot": None,
    "Specimen": None,
    "StructureDefinition": None,
    "StructureMap": None,
    "Subscription": None,
    "Substance": None,
    "SupplyDelivery": None,
    "SupplyRequest": None,
    "Task": None,
    "TestReport": FHIR_Infrastructure_type,
    "TestScript": FHIR_Infrastructure_type,
    "ValueSet": FHIR_Infrastructure_type(),
    "VisionPrescription": FHIR_Observation_type("patient", "encounter", "prescriber")
}