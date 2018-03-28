# Command line script tests


| File | Test | Function | Dependencies |
| ---- | ---- | -------- | -------- |
| test_concept_coverage.py | test_concept_coverage | Determine whether there are any concept codes referenced in the `observation_fact` table that don't exist in the `concept_dimension` table. | |
| | test_modifier_coverate | Determine whether there are any modifier codes in the `observation_fact` table that don't have matching codes in the `modifier_dimension` table. | |
| | test_ontology_coverage_1 | Determine whether there are any queries in the `ontology_table` that do not reference concepts in the `concept_dimension` table | |
| | test_ontology_coverage_2 | Determine whether there are any `concept_dimension` entries that don't have corresponding entries in the `ontology_table` | |
| | test_ontology_coverage_3 | Determine whether there are any *leaf* queries in the `ontology_table` that do not reference concepts in the `modifier_dimension` table. Note that non-leaf (draggable) queries may well not | |
| | test_ontology_coverage_4 | Determine whether there are any `modifier_dimension` entries that don't have corresponding entries in the `ontology_table` | |
| test_loadfacts_script.py | test_no_args | Test the output of loadfacts when invoked with no arguments | data_out/loadfacts/noargs |
| | test_no_input | Test the error message where no input is supplied | data_out/loadfacts/noinput | 
| | test_help | Test the "-h" output | data_out/loadfacts/help |
| test_loadfacts_patientdimension.py | test1 | Load `data/medicationdispense0308.ttl`. **Note:** this test is incomplete and is currently skipped | data/medicationdispense0308.ttl |
|  | test2 | Load `http://hl7.org/fhir/Patient/pat1`. **Note:** this test is incomplete and is currently skipped | dhttp://hl7.org/fhir/Patient/pat1 |
| test_removefacts_script.py | test_no_args | Test the output of removefacts when invoked with no arguments | data_out/removefacts/noargs |
| | test_help | Test the help output | data_out/removefacts/help | 
| | test_onearg | Test output when supplied with one upload_id | data_out/removefacts/onearg |
| | test_threeargs | Test output when supplied with 3 upload identifiers | data_out/removefacts/threeargs |
| | test_config_params | test with config file | data/db_conf |
| | | | data_out/removefacts/confparms |
| test_generate_i2b2.py | | | |
| test_generate_i2b2_script.py | test_no_args | Invocation with no arguments | data_out/generatei2b2/noargs|
| | test_help | generate_i2b2 -h |data_out/generatei2b2/help |
| | test_version | generate_i2b2 -v |data_out/generatei2b2/version |
| | test_test | generate_i2b2 --conf (conf) --test | data_out/generatei2b2/list
| | | | tests/conf/db_conf |



## Notes:
1) `test_concept_coverage.py` should be turned into an actual script, as this isn't really a development unit test, but a test of the state of a set of i2b2 tables.

## TODO:
1 ) complete test_patientdimension.py


