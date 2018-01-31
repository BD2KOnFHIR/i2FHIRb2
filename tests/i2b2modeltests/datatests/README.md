# i2b2 data model tests
This module contains tests for the i2b2 model tools

| File | Test | Function | Dependencies |
| ---- | ---- | -------- | -------- |
| test_encounter_mapping_sql.py | test_insert | Remove all entries for the default upload identifier (41712) and then test `EncounterMapping()` constructor | |
| test_i2b2codes.py | test_codes | Test the i2b2 demographics (`DEM &#124; AGE:`, etc.) | |
| test_observation_fact.py | test_basics | Test the `ObservationFact()` constructor | |
| | test_fhirobservationfact | Test the `FHIRObservationFact()` constructor | http://build.fhir.org/observation-example-bmi.ttl |
| | test_complete_fact_list | Test `FHIRObservationFactFactory` | http://build.fhir.org/observation-example-bmi.ttl |
| | | | data/test_complete_fact_list.tsv |
| test_observation_fact_sql.py | test_insert | Test ObservationFact `delete_upload_id` and `add_or_update_records` functions | |
| test_patient_dimension.py | test_basics | Test `PatientDimension()` constructor and accessor functions | |
| test_patient_dimension_sql.py | test_insert | Test PatientDimension `delete_upload_id` and `add_or_update_records` functions | |
| test_patient_mapping.py | test_patient_mapping | Test `PatientMapping()` constructor | |
| test_patient_mapping_sql.py | test_insert | Test PatientMapping `delete_uploadd` and `add_or_update_records` functions | |
| test_visit_dimension.py | test_basics | Test `VisitDimension()` constructor | |
| test_visit_dimension_sql.py | test_insert |  Test VisitDimension  `delete_uploadd` and `add_or_update_records` functions | |


