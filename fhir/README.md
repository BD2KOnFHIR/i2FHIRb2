# FHIR Profile Maps
This directory carries a set of proposed additions to the FHIR core profiles to include i2b2 mappings.  In the i2b2 context, FHIR resources can:
* Load directly into the `observation_fact` table.  This option is used for patient-focused resources such as Observation, DiagnosticReport, Condition, Encounter, MedicationRequest, etc.
* Be mapped into the `patient_dimension` table.  This option is used for Patient resources, although it may also be possible for *some* of the data in a Patient resource to be considered "observations" as well. (TBD)
* Be mapped into the `visit_dimension` table.
* Be mapped into the `provider_dimension` table. The FHIR Organization resource, in particular, would fit this situation.
* Load into other fact tables (we need to review the FHIR OMOP distro for details)
* Not load at all

## Approaches
1) The first approach would be to include the mappings in the actual FHIR core distributions and, where necessary, the profiles.  [patient.profile.xml](patient.profile.xml) represents a partial example of how this would look.  Note that we still have to add FHIR metadata for the `i2b2` mapping identity.
2) A second approach would be to convert 