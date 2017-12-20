# Test cases for reported issues

| File | Test | Function | Dependencies |
| ---- | ---- | -------- | -------- |
| test_conf_parser.py | test1 | Test that the file names pulled from the config file are relative to the file itself while the ones referenced directly are relative to the script itself. | ../../tests/data/synthea_data/fhir/Zieme803_Caroline16_2.json |
| | | | ../../tests/conf/db_conf |
| test_decimal_datatype.py | test_decimal_literal | Demonstrate that quoted literals with different degrees of precision are not considered equal while their unquoted counterparts are.  (Part of a general issue involving FHIR and decimal precision | |
| test_observation_component | test_boyle | Make sure that the `instance_num` of the systolic bp is different than the diastyolic bp and that the codes and values have the same instance numbers | tests/data/fhir_metadata_vocabulary/fhir.ttl |
| | | | tests/conf/db_conf |
| | | | ./data/Boyle963_Kathleen891_83.ttl |
| | | | data_out/observation_fact.tsv |
| | test_issue_6 | Verify that, for all non-zero instances, the same number has the same concept code. | tests/data/fhir_metadata_vocabulary/fhir.ttl |
| | | | tests/conf/db_conf |
| | | | ./data/Boyle963_Kathleen891_83.ttl |
| | | | data_out/observation_fact.tsv |
| test_primitive_types.py | test_primitive | Test various FHIR types as primitive | |
| test_status_code_errors.py | test_active_status_code | Tests for the visit dimension `ActiveStatusCd` | |
| | test_vital_status_code | Tests of the patient dimension `VitalStatusCd` | |
