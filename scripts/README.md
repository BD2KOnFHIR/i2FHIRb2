# Command Line Conversion Tools

The scripts directory contains three command line utilities:

1) [generate_i2b2](generate_i2b2.md) -- load the FHIR Metadata Vocabulary (fhir.ttl) into the
`concept_dimension`, `modifier_dimension` and ontology tables.
2) [jsontordf](jsontordf.md) -- convert FHIR JSON into FHIR RDF
3) [loadfacts](loadfacts.md) -- load FHIR JSON or FHIR RDF into the i2b2 observation_fact,
patient_dimension, visit_dimension, patient_mapping and encounter_mapping tables.
4) [removefacts](removefacts.md) -- remove the records specified by a particular `upload_id` from the observation_fact and associated tables.
5) [conf_file](conf_file.md) -- generate configuration files for frequently used parameters.