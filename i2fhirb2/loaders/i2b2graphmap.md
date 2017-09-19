# i2b2graphmap.py

## Summary
The `I2B2GraphMap` class converts an RDF graph containing a collection of FHIR resources, collections and/or bundles into a set of i2b2 crc table entries.  For every subject in the graph that has an `rdf:type` in the [FHIR_RESOURCE_MAP](../fhir/fhirresourcemap.py) table it converts set of triples associated with that subject into a corresponding set of `observation_fact`, `patient_dimension / patient_mapping` or `visit_dimension / visit_mapping` entries.

See also: [FHIR_RESOURCE_MAP documentation](../fhir/fhirresourcemap.md).

## Methods
### `generate_tsv_files()`
Emit the various i2b2 table entries as tab separated value (.tsv) files in the output directory (`opts.outdir`) specified in the supplied options.

### `load_i2b2_tables()`
1) If requested (`opts.remove == True`)elete any existing records in the i2b2 tables having an `upload_id` that matches `opts.uploadid`.
2) Add or update the corresponding i2b2 crc tables.

### `summary()`
Return a textual summary of the number of resources of various types that were generated or skipped.

## Notes
1) The record deletion process needs to be embedded in a transaction boundary.  At the moment, it is possible to empty a set of records with a given upload_id if an error occurs in the load step.
2) The `visit_dimension` and `provider_dimension` maps still need to be implemented.
