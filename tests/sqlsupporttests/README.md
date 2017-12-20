# Tests for the SQL support functions
This directory tests the functionality in `i2fhirb2.sqlsupport`

| File | Test | Function | Dependencies |
| ---- | ---- | -------- | -------- |
| test_dbconnection.py | test_decodefileargs1 | Test `dbconnection.add_connection_args` and `dbconnection.decode_file_args` | tests/conf/db_conf |
| | test_decodefileargs2 | Test database specific overrids in `dbconnection.decode_file_args` | tests/conf/db_conf_2 |
| test_dynamic_object | test_basics | Various tests for the dynamic object implementation | |
| | test_inheritence | | |
| | test_overrides | | |
| | test_instance_setting | | |
| | test_null_text | | |
| test_i2b2_tables | test_basics | Test basic table access by looking at the keys and running a query on the `concept_dimension` table
| | test_as_dict | verify that logical table names can be mapped to physical and that getattr works for tables |

## TODO:
1) Dynamic objects need to be more completely documented and either:
   1) Formed into a separate package for general use with all sorts of SQL or
   2) Replaced with a SQLAlchemy equivalent if such a thing exists