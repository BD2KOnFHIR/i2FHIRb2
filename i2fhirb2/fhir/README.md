# FHIR mapping to i2b2 Tables
## Resource to i2b2 type map
[fhirresourcemap.py](fhirresourcemap.py) contains a map from the FHIR resource type to the corresponding i2b2 entry.
 As an example, the snipped below states that the FHIR Account resource is mapped to the I2B2 observation fact table, the 

```python
FHIR_RESOURCE_MAP: Dict[URIRef, Optional[FHIR_Resource_type]] = {
    FHIR.Account: FHIR_Observation_Fact_type(FHIR.Account.subject, None, FHIR.Account.owner),
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
    FHIR.CarePlan: FHIR_Observation_Fact_type(FHIR.CarePlan.subject, FHIR.CarePlan.context, None),
```