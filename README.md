# i2FHIRb2 - FHIR in i2b2

## Introduction
This package creates an i2b2 ontology from the FHIR STU3 resource model.  It uses a combination of the [FHIR W5 (who, what, why, where, when) ontology](http://build.fhir.org/w5.ttl) and the [FHIR Resource Model Ontology](http://build.fhir.org/fhir.ttl) to create an i2b2 equivalent.

## Installation
1) Clone or download this package from [https://github.com/BD2KOnFHIR/i2FHIRb2](https://github.com/BD2KOnFHIR/i2FHIRb2)
   ```bash
   > git clone https://github.com/BD2KOnFHIR/i2FHIRb2
   > cd i2FHIRb2
    ```
## Loading the i2b2 ontology and concept/modifier dimension tables
This package is still under development has only been tested with PostgreSQL.  At the moment, it assumes that the PostgreSQL is running locally at the standard coordinates, `jdbc:postgresql://localhost:5432/i2b2`.  For details on how to load the tables directly, see: [Running the conversion utility](#Running the conversion utility).

We also supply tab-separated-value (tsv) tables that (theoretically) can be loaded into any existing implementation.  

**NOTE**: Before you load the files below, you need to adjust the length of the following columns:
<table>
<tr>
<td><b>table</b></td>
<td><b>column</b></td>
<td><b>default size</b></td>
<td><b>new size</b></td>
</tr>
<tr>
<td>concept_dimension</td>
<td>concept_cd</td>
<td>50</td>
<td>200</td>
</tr>
<tr>
<td>modifier_dimension</td>
<td>modifier_cd</td>
<td>50</td>
<td>200</td>
</tr>
<tr>
<td>custom_meta</td>
<td>c_basecode</td>
<td>50</td>
<td>200</td>
</tr>
<tr>
<td></td>
<td>c_tooltip</td>
<td>900</td>
<td>1600</td>
</tr>
</table>

### TSV Files


* **`table_access.tsv`** -- the `table_access` table describes the location and root paths of i2b2 metadata.  This file has one row that states that FHIR resource definitions can be found in the `custom_meta` table with the root '\\FHIR\\'.
* **`concept_dimension.tsv`** --  the `concept_dimension` table links defines the set of possible concept codes that can appear in the `observation_fact` table.  For FHIR, this includes all "first level" resource entries -- Observation.identifier, Observation.basedOn, etc.
* **`modifier_dimension.tsv`** -- the `modifier_dimension` table contains possible modifier codes for the `observation_fact` table.  For FHIR, this contains the substructure represented in the concept codes -- `CodeableConcept.text`, `CodeableConcept.coding`, etc.
* **`ontology.tsv`** -- the "ontology" or "metadata" tables provide a navigational hierarchy that serve to organize and group i2b2 dimensions (`concept`, `modifier`, `patient`, `provider` and `visit`).  The **`i2FHIRb2`** project uses the FHIR W5 tables to provide high level organization and then lists the resources and their possible properties and modifiers for this table.

All of these tables have tab-separated values and the first row of each table has the column headers.   They can be imported directly into the corresponding i2b2 tables

<sub>**NOTE:** We have been unable to convince the postgreSQL import tool to represent empty columns as `NULL` values.  While, in beneral, the i2b2 software appears to treat Nulls and zero-length strings as equivalent, there is at least one place where this breaks -- the `m_exclusion_cd` column in the `custom_meta` (ontology) table. After loading the `ontology.tsv` table it is necessary to execute the following SQL:
 ```sql
 UPDATE custom_meta SET m_exclusion_cd = NULL WHERE m_exclusion_cd = '';
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
   (venv) > pip install -e .
   ```
   (Don't miss the '.' in the above command)
3) Validate the installation
    ```bash
    (venv) > generate_i2b2 -h
 
    usage: generate_i2b2 [-h] [-o OUTDIR] [-t TABLE] [-r RESOURCE]
                     [-s SOURCESYSTEM] [-b BASE] [-l]
                     indir

    FHIR in i2b2 generator

    positional arguments:
       indir                 Input directory or URI of w5.ttl and fhir.ttl files

    optional arguments:
        -h, --help            show this help message and exit
       -o OUTDIR, --outdir OUTDIR
                               Output directory to store .tsv files
       -t TABLE, --table TABLE
                               Table to update (e.g. concept_dimension) - default is
                        all tables
       -r RESOURCE, --resource RESOURCE
                               Name of specific resource to emit (e.g. Observation) -
                        default is all
       -s SOURCESYSTEM, --sourcesystem SOURCESYSTEM
                               sourcesystem code. Default: 'FFHIR STU3'
       -b BASE, --base BASE  Concept dimension and ontology base path.
                               Default:\FHIR\
       -l, --load            Load i2b2 SQL tables
   ```
4) Creating the i2b2 metadata

    This package is still under development has only been tested with PostgreSQL.  At the moment, it assumes that the PostgreSQL is running locally at the standard coordinates, `jdbc:postgresql://localhost:5432/i2b2`.
    ```bash
    (venv) > generate_i2b2 tests/data -l
    Loading fhir.ttl
    loading w5.ttl
    1 i2b2metadata.table_access record inserted
    Changing length of concept_dimension.concept_cd from 50 to 200
    1478 i2b2demodata.concept_dimension records inserted
    Changing length of modifier_dimension.modifier_cd from 50 to 200
    7682 i2b2demodata.modifier_dimension records inserted
    Changing length of custom_meta.c_basecode from 50 to 200
    Changing length of custom_meta.c_tooltip from 700 to 1600
    15523 i2b2metadata.custom_meta records inserted
    ```


## Current State of the Project

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
* FHIR values -- the number of possible types for FHIR `value[x]` entries is sizeable.  Expanding each of these as URI's can potentially expand the size of the ontology table by an order of magnitude.  We need to decide what to do about the values and core data types.  One possibility would be a plug-in similar to the existing lab-value plug in.



### FHIR Ontology Issues
1) The current W5 ontology is missing `w5:when`
2) The W5 root is defined as an `owl:OntologyEntry`.  We need to model this correctly -- should it be a root class or, an entity whose *members* are the root classe?
3) Parts of W5 use a nested notation (`who.actor`, `when.done`) while others don't (`device`, `diagnostics`).  FHIR uses nested notation throughout (`administrative.device`, `clinical.diagnostics`)
4) The naming convention in `fhir.ttl` turns out not to be unique.  As an example, `ExplanationOfBenefit`, `Claim`, and `ClaimResponse` all have `item` elements which all get mapped to a single type, `ItemComponent` despite the fact that each type is significantly different.  This problem will occur whenever there are embedded `BackboneElements` having the same name.