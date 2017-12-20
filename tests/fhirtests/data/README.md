# Data for fhirtests
| File | Used by  | Purpose |
| ---- | -------- | ------- |
|diagnosticreport-example-f202-bloodculture.ttl | test_fhir_visitdimension.py | testing visit_dimension / encounter_mapping from a non-patient resource |
|fhir_concept_dimension_domain_resource | test_fhir_ontology.py | Expected concept_dimension output for FHIR.DomainResource |
|fhir_concept_dimension_observation.tsv | test_fhir_ontology.py | Expected concept_dimension output for FHIR.Observation |
|fhir_concept_dimension_resource.tsv | test_fhir_ontology.py | Expected concept_dimension output for FHIR.Resource |
|fhir_modifier_dimension_domain_resource | test_fhir_ontology.py | Expected modifier_dimension output for FHIR.DomainResource |
|fhir_modifier_dimension_observation.tsv | test_fhir_ontology.py | Expected modifier_dimension output for FHIR.Observation |
|fhir_modifier_dimension_resource.tsv | test_fhir_ontology.py | Expected modifier_dimension output for FHIR.Resource |
|fhir_observation_resource_graph.txt | test_fhirmetadatavocabulary.py | output of the FHIRMetadataVocabulary.resource_graph for the FHIR.Observation resource |
|fhir_ontology_domain_resource | test_fhir_ontology.py | Expected ontology_table output for FHIR.DomainResource |
|fhir_ontology_observation.tsv | test_fhir_ontology.py | Expected ontology_table output for FHIR.Observation |
|fhir_ontology_resource.tsv | test_fhir_ontology.py | Expected ontology_table output for FHIR.Resource |
|fhir_resource_concepts.txt | test_fhirmetadatavocabulary.py | Output of the FHIRW5Ontology.fhir_resource_concepts function |
|patient-example.ttl | test_fhir_patientdimension.py | Example input to test patient dimension and patient mapping load |
|patient-example-deceased_bool.ttl | test_fhir_patientdimension | Test of a patient with a deceasedBoolean entry |
|w5_graph.txt | test_fhirmetadatavocabulary.py | Output of the FHIRW5Ontology.w5_graph function |