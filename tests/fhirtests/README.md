# Test the FHIR table loaders

| File | Test | Function | Dependencies |
| ---- | ---- | -------- | -------- |
| test_composite_uri.py | test1 | Test fhirspecific.composite_uri function | (none) |
| test_encounter_mapping.py | test_encounter_mapping | Test EncounterMapping constructor | (none) |
| test_fhir_codemapping.py | test_value_string | Test of FHIR string value types | (none) |
| | test_value_quantity_units | Test FHIR SimpleQuantity units variations | |
| | test_value_quantity | Test FHIR SimpleQuantity values | | 
| | test_value_integer | Test FHIR Integer values | |
| | test_value_codeable_concept_1 | Basic codeable concept tests. (See: test_fhir_codemapping.py for more details) | |
| | test_value_codeable_concept_2 | Test of multiple observation component coding | | 
| test_fhir_encounter_mapping.py | test_basic_mapping | Test FHIREncounterMapping constructor | (none) |
| | test_encounternum_refresh | Test the EncounterNumberGenerator |  (none) |
| test_fhir_observation_fact.py | test_fhirobservationfact | Test the `FHIRObservationFact()` constructor | http://build.fhir.org/observation-example-bmi.ttl |
| | | | data/test_complete_fact_list.tsv
| test_fhir_ontology.py | test_concept_dimension | Test Observation resource representation in concept_dimension table | fhir_concept_dimension_domain_resource.tsv |
| | | |fhir_concept_dimension_observation.tsv |
| | | |fhir_concept_dimension_resource.tsv |
| | test_modifier_dimension | Test Observation resource representation in modifier_dimension | fhir_modifier_dimension_domain_resource.tsv|
| | | |fhir_modifier_dimension_observation.tsv |
| | | |fhir_modifier_dimension_resource.tsv |
| | test_ontology | Test Observation resource representation in ontology_table | fhir_ontology_observation.tsv |
| | | |fhir_ontology_observation.tsv |
| | | |fhir_ontology_resource.tsv |
| test_fhir_ontology_part2.py | test_fhir_resource_concepts | Test the list of FHIR resource concepts | data/fhir_resource_concepts.txt |
| | test_resource_graph | Test of resource graph using W5 | data/fhir_observation_resource_graph.txt |
| test_i2b2_ontology | test_concept_ontology_entry | Test the `ConceptOntologyEntry` constructor | |
| | test_modifier_ontology_entry | Test the `ModifierOntologyEntry` constructor | |
| | test_ontology_root | Test the OntologyRoot constructor | |
| | test_ontology_root | Test the `OntologyRoot` constructor | |
| test_fhir_patientdimension.py | test_load_ttl | Load patient-example.ttl into FHIRPatientDimension and validate the resulting patient_dimension and both patient_mapping entries | patient-example.ttl |
| | test_patient_death_dates | Test various death date formats (Not complete) | patient-example-deceased_bool.ttl |
| test_fhir_patientmapping.py | test_patient_mapping | Test FHIRPatientMapping constructor | (none) |
| test_fhir_primitivetypes.py | test_primitive_types | Test loading of all FHIR primitive types | data/primitivetypes.ttl |
| | test_patientnum_refresh | Test PatientNumberGenerator (test is fragile at the moment) | (none) 
| test_fhir_visitdimension.py | test_load_ttl | Load a sample DiagnosticReport and validate the resulting EncounterMapping and VisitDimension entries | diagnosticreport-example-f202-bloodculture.ttl |
| test_fhirmetadatavocabulary.py | test_w5_graph | Test the w5 graph against a fixed value (this will need to be fixed whenever the contents of w5 and/or the number of FHIR resources changes) | tests/data/fhir_metadata_vocabulary/fhir.ttl |
| | | | tests/data/fhir_metadata_vocabulary/w5.ttl |
| | test_fhir_resource_concepts | test the fhir_resource_concepts function | " |
| | test_resource_graph | test the resource_graph function using the FHIR.Observation resource | " |
| test_fhir_specific.py | test_is_w5_uri | | (None) |
| | test_composite_uri | | (None) |
| | test_modifier_name | | (None) |
| | test_modifier_code | | (none) |
| | test_rightmost_element | | (none) |
| | test_modifier_path | | shared_graph (FHIRGraph() |
| | test_concept_name | | (none) |
| test_full_paths.py | (OBSOLETE) | | |
| test_metadata_xml | test_basics | Test the metadata_xml function -- generating the appropriate metadata for the various data types. | (None) |
| test_w5ontology.py | test_w5_concepts | test the w5_concepts_function | tests/data/fhir_metadata_vocabulary/w5.ttl |
| | test_w5_paths | test the w5_paths function | tests/data/fhir_metadata_vocabulary/w5.ttl |
| | test_full_w5_paths | test the w5_paths function in conjunction with the fhir.ttl ontology | tests/data/fhir_metadata_vocabulary/w5.ttl |
| | | | tests/data/fhir_metadata_vocabulary/fhir.ttl |

