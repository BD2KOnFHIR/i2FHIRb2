# FHIR mapping to i2b2 Tables
## Resource to i2b2 type map
[fhirresourcemap.py](fhirresourcemap.py) contains a map from the FHIR resource type to the corresponding i2b2 entry.
 As an example, the snipped below states:
 * The FHIR [Account](http://hl7.org/fhir/account.html) resource represents a set of observation facts, where the `fhir:Account.subject` is the patient id, there is no encounter identifier and the `fhir:Account.owner` tag carries the provider identifier.
 * The FHIR [Organization](http://hl7.org/fhir/organization.html) resource maps to the provider dimension. (Still to be implemented)
 * The FHIR [Patient](http://hl7.org/fhir/patient.html) resource maps to the patient dimension
 * The FHIR [Bundle](http://hl7.org/fhir/bundle.html) resource is a bundle (collection of resources) - entries *in* the bundle are mapped to i2b2, but the bundle itself is not.
 * The FHIR [CapabilityStatement](http://hl7.org/fhir/capabilitystatement.html) is part of the FHIR infrastructure and has no representation in the i2b2 space
* The FHIR [Encounter](http://hl7.org/fhir/encounter.html) resource maps to the visit dimension (Still to be implemented)
* The FHIR [EpisodeOfCare](http://hl7.org/fhir/episodeofcare.html) resource has not yet been mapped
```python
from typing import Dict, Optional
from rdflib import URIRef
from i2fhirb2.fhir.fhirresourcemap import FHIR_Resource_type, FHIR_Observation_Fact_type, FHIR_Bundle_type, FHIR_Visit_Dimension_type, FHIR_Provider_Dimension_type, FHIR_Patient_Dimension_type, FHIR_Infrastructure_type
from fhirtordf.rdfsupport.namespaces import FHIR

FHIR_RESOURCE_MAP: Dict[URIRef, Optional[FHIR_Resource_type]] = {
    FHIR.Account: FHIR_Observation_Fact_type(FHIR.Account.subject, None, FHIR.Account.owner),
    FHIR.Organization: FHIR_Provider_Dimension_type(),
    FHIR.Patient: FHIR_Patient_Dimension_type(),
    FHIR.Bundle: FHIR_Bundle_type,
    FHIR.CapabilityStatement: FHIR_Infrastructure_type(),
    FHIR.Encounter: FHIR_Visit_Dimension_type(FHIR.Encounter.subject),
    FHIR.EpisodeOfCare: None,
}
```