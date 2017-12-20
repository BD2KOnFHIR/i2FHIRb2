# Dimension table loading for FHIR

## `concept_dimension`

A concept_dimension entry is created for every non-modifier leaf node in the ontology table (c_visualattributes = 'LA').

The purpose of the concept_dimension table is to map paths from the ontology table to sets of concept codes.  For the FHIR use case, this mapping will always be 1:1, as we use the modifier codes to generate multiple entries.  

As an example, the ontology table entries:

| c_fullname | c_visualattributes | c_tablename | c_facttablecolumn | c_operator | c_dimcode |
| --- |---|---|---|---|---|
| \FHIR\clinical\diagnostics\Observation\ | CA | | | | |
| \FHIR\clinical\diagnostics\observation\code\ | FA | | | |
| \FHIR\clinical\diagnostics\Observation\effectiveDateTime\ |LA | concept_dimension | concept_cd | = | \FHIR\Observation\effectiveDateTime\ |

Would have the following entries in the `concept_dimension` table:

| concept_path| concept_cd |
|---|---|
| \FHIR\Observation\effectiveDateTime\ | FHIR:Observation.effectiveDateTime |

As a result, if the usere were to select an the `effectiveDateTime` ontology entry, the resulting query would include, in part an element of the form:

```text
observation_fact.concept_cd in (SELECT concept_cd from concept_dimension where concept_path = '\FHIR\Observation\effectiveDateTime\'
```

Note:  We *could* simplfy this for performance reasons -- `select '\FHIR\Observation\effectiveDateTime\' from (some table)`


## `modifier_dimension`
The `modifier_dimension` table is where the majority of the "heavy lifting" gets done in the FHIR situation.

| depth | c_fullname | c_visualattributes | c_tablename | c_facttablecolumn | c_operator | c_dimcode | m_applied_path |
| --- |---|---|---|---|---|---|---|
| 4 | \FHIR\clinical\diagnostics\Observation\code\ | FA | | | | | @ |
| 5 | \FHIR\clinical\diagnostics\Observation\code\coding\ | FA | | | | | @ |
| 1 | \FHIRMod\Observation\code\text\ | RA | modifier_dimension | modifier_path | like | \FHIR\CodeableConcept\text\ | \FHIR\clinical\diagnostics\Observation\code\ |
| 1 | \FHIRMod\Observation\code\coding\system\ | RA | modifier_dimension | modifier_path | like | \FHIR\Coding\system\ | \FHIR\clinical\diagnostics\Observation\code\coding\ |
| 1 | \FHIRMod\Observation\code\coding\code\ | RA | modifier_dimension | modifier_path | like | \FHIR\Coding\code\ | \FHIR\clinical\diagnostics\Observation\code\coding\ |


