# i2FHIRb2 - FHIR in i2b2

## Introduction
This package creates an i2b2 ontology from the FHIR STU3 resource model.  It uses a combination of the [FHIR W5 (who, what, why, where, when) ontology](http://build.fhir.org/w5.ttl) and the [FHIR Resource Model Ontology](http://build.fhir.org/fhir.ttl) to create an i2b2 equivalent.

## Installation
1) Clone or download this package from [https://github.com/BD2KOnFHIR/i2FHIRb2](https://github.com/BD2KOnFHIR/i2FHIRb2)
   ```bash
   > git clone https://github.com/BD2KOnFHIR/i2FHIRb2
   > cd i2FHIRb2
    ```
## Loading the data into i2b2
This package is still under development.  Eventually, we intend to be able to load date directly into an i2b2 instance but, at the moment, we generate a set of tab seperated value (tsv) tables that will need to be imported into an i2b2 instance. These tables can be found in the `i2b2files` directory.

* **`table_access.tsv`** -- the `table_access` table describes the location and root paths of i2b2 metadata.  This file has one row that states that FHIR resource definitions can be found in the `custom_metadata` table with the root '\\FHIR\\'.
* **`concept_dimension.tsv`** --  the `concept_dimension` table links defines the set of possible concept codes that can appear in the `observation_fact` table.  For FHIR, this includes all "first level" resource entries -- Observation.identifier, Observation.basedOn, etc.
* **`modifier_dimension.tsv`** -- the `modifier_dimension` table contains possible modifier codes for the `observation_fact` table.  For FHIR, this contains the substructure represented in the concept codes -- `CodeableConcept.text`, `CodeableConcept.coding`, etc.
* **`ontology.tsv`** -- the "ontology" or "metadata" tables provide a navigational hierarchy that serve to organize and group i2b2 dimensions (`concept`, `modifier`, `patient`, `provider` and `visit`).  The **`i2fhirb2`** project uses the FHIR W5 tables to provide high level organization and then lists the resources and their possible properties and modifiers for this table.

All of these tables have tab-separated values and the first row of each table has the column headers.   They can be imported directly into the corresponding i2b2 tables

<sub>**NOTE:** We have been unable to convince the postgreSQL import tool to represent empty columns as `NULL` values.  While, in beneral, the i2b2 software appears to treat Nulls and zero-length strings as equivalent, there is at least one place where this breaks -- the `m_exclusion_cd` column in the `custom_metadata` (ontology) table. After loading the `ontology.tsv` table it is necessary to execute the following SQL:
 ```sql
 UPDATE custom_metadata SET m_exclusion_cd = NULL WHERE m_exclusion_cd = '';
 ```
</sub>



### Dependencies
This package uses Python 3 and has been tested with Python 3.6.1

## Running the conversion utility
1) (Optional) Create a virtual environment:
    ```bash
    > virtualenv venv -p python3
    > . venv/bin/activate
    (venv) > 
    ```
2) Install dependencies, etc. In the root project directory (i2FHIRb2):
    ```bash
   (venv) > pip setup.py -e .
   ```
3) Validate the installation
    ```bash
    (venv) > generate_i2b2 -h
 
    usage: generate_i2b2 [-h] [-r RESOURCE] [-s SOURCESYSTEM] [-b BASE]
                         indir outdir
    
    FHIR in i2b2 generator
    
    positional arguments:
      indir                 Input directory or URI of w5.ttl and fhir.ttl files
      outdir                Output directory to store .tsv files
    
    optional arguments:
      -h, --help            show this help message and exit
      -r RESOURCE, --resource RESOURCE
                            Name of specific resource to emit (e.g. Observation) -
                            default is all
      -s SOURCESYSTEM, --sourcesystem SOURCESYSTEM
                            sourcesystem code. Default: 'FFHIR STU3'
      -b BASE, --base BASE  Concept dimension and ontology base path.
                            Default:\FHIR\ 
   ```
  
**Note:** The `w5.ttl` file has been edited to fix a couple of issues described below.  Until we get this fix installed in the FHIR distribution, it will be necessary to use the local file.


## Current State of the Project
### concept_dimension 
1) At the moment, this package generates concept_dimension entries for *all* FHIR and W5 concepts.  It turns out that, while it appears to be necessary to have a dimension query in the ontology table, this query does not have to be resolvable in the case of "Container" (`c_visualattributes='CA'`) items.  We plan to remove all container level entries.
### modifier_dimension
1) At the moment we only generate entries for FHIR elements that have defined URI's in the FHIR ontology (`fhir.ttl`).  This means, however, that there is NOT a modifier code for the Coding.code (`fhir:Coding.code`) element in the CodeableConcept.coding (`fhir:CodeableConcept.coding`) element in the Observation code (`fhir:Observation.code`).  We plan to create a set of flattened modifier URI's (e.g. `fhir:CodeableConcept.coding.code`, `fhir:Observation.component.value.coding.code`, etc.)
### metadata
1) coded elements
   * Required FHIR coded elements could be represented as Enums.  An alternative is to represent each possible code as a discrete concept / modifier code.  A second alternative is to use the Enum value picker.
   * Non-required FHIR coded elements are both underspecified and too numerous to be represented as enums OR discrete codes (?). Choices include:
       * Update the ontology as data is entered - only include *actual* codes in the information
       * Connect up to a terminology server (!)
       
### dimensions
The project currently assumes that all information appears in the `observation_fact` table.  This obviously isn't the case as:
* Patient / provider / visit information either maps to or extends the i2b2 dimension tables
* Resources such as 'Device', 'Medication', etc. currently have no place in i2b2 at all.



## Issues
### Representational Issues
* Dates and times -- there doesn't appear to be an i2b2 plugin for selecting date and time values for entries in the fact table
* FHIR values -- the number of possible types for FHIR `value[x]` entries is sizeable.  Expanding each of these as URI's can potentially expand the size of the ontology table by an order of magnitude.  We need to decide what to do about the values and core data types.  One possibility would be a plug-in similar to the existing lab-value plug in.



### FHIR W5 Ontology Issues
1) The current W5 ontology is missing `w5:when`
2) The W5 root is defined as an `owl:OntologyEntry`.  We need to model this correctly -- should it be a root class or, an entity whose *members* are the root classe?
3) Parts of W5 use a nested notation (`who.actor`, `when.done`) while others don't (`device`, `diagnostics`).  FHIR uses nested notation throughout (`administrative.device`, `clinical.diagnostics`)