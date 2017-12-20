# i2b2 metadata model tests

| File | Test | Function | Dependencies |
| ---- | ---- | -------- | -------- |
| test_concept_dimension.py | test_basics | Test `ConceptDimension` constructor | |
|  | test_interactions | Make sure that `ConceptDimension` and `ModifierDimension` don't change each other's content do to the `CommonDimension` root. | |
| | test_fhir_conceptdimensionroot | Test the concept dimension root concept. **Note:** This function may not be necessary. | |
| test_dimension_query.py | test_concept_query | Test the `ConceptQuery` constructor. | |
| | test_empty_query | Test the `EmptyQuery` (non-query) constructor | |
| | test_modifier_query | test the `ModifierQuery` constructor | |
| | test_patient_query | test the `PatientQuery` constructor | |
| | test_visit_query | Test the `VisitQuery` constructor | | 
| test_i2b2_ontology | test_basics | Test the `OntologyEntry` constructor (an entry in the ontology table) | |
| | test_concept_ontology_entry | Test the `ConceptOntologyEntry` constructor | |
| | test_modifier_ontology_entry | Test the `ModifierOntologyEntry` constructor | |
| | test_ontology_root | Test the `OntologyRoot` constructor | |
| test_modifier_dimension.py | test_basics | test the `ModifierDimension` constructor | |
| test_table_access.py | test | Test `TableAccess()` | |
| test_visual_attributes.py | test_visual_attributes | Test the VisualAttributes for the i2b2 ontology table | |