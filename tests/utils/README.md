# Testing Support Utilities

| File | element | Function | Dependencies |
| ---- | ---- | -------- | -------- |
| base_test_case.py | test_directory | absolute path to the tests directory | |
| | test_conf_directory | absolute path to the tests/conf directory | |
| | test_data_directory | absolute path to the tests/data directory | |
| | mvdir | absolute path to the tests/data/fhir_metadata_vocabulary directory |
| | FHIRGraph() | Return an `rdflib` Graph that contains {mvdir}/fhir.ttl  | |
| | BaseTestCase() | Mixin to support almostnow and almostequal assertions | |
| | make_and_clear_directory | Function that safely creates a test directory. If the target directory doesn't exist, it will be created and a file named 'generated' will be added to it.  If it does exist, the directory will be cleared *as long as the 'generated' file is present*. | |
| connection_helper.py |connection_helper() | Create an i2b2 table connection using the contents of db_conf in the test configuration directory and upload id 41712.  **Warning:** do NOT use 41712 in every day uploads -- the tests remove this. | tests/conf/db_conf|
| shared_graph.py | shared_graph | A globally available instance of FHIRGraph | tests/data/fhir_metadata_vocabulary |
