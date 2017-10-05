# i2FHIRb2 - FHIR in i2b2

## Introduction
This package creates an i2b2 ontology from the FHIR STU3/R4 resource model.  It uses a combination of the [FHIR W5 (who, what, why, where, when) ontology](http://build.fhir.org/w5.ttl) and the [FHIR Resource Ontology](http://build.fhir.org/fhir.ttl) to create an i2b2 equivalent.

    
## i2b2 requirements
i2FHIRb2 has been tested with the postgres version of [i2b2 Software](https://www.i2b2.org/software/) release 1.7.08.  While it will theoretically
work with earlier versions, you may encounter issues, including:
1) The FHIR data includes UTF-8 characters.  Earlier releases of the i2b2 used `SQL_ASCII` encoding which won't work.
2) This package hasn't been tested with Oracle or Microsoft SQL Server.  We use [sqlalchemy](http://www.sqlalchemy.org/),
 which should minimize the issues, but you may want to talk with the authors before attempting to run with a 
 non-postgres back end.

Before you start, you will need to know:
1) The ip and port of the i2b2 SQL server.  The default for postgres is: **localhost:5432**
2) A userid/password combination that has write access to the `i2b2demodata` (CRC) and `i2b2metadata` schemas.  The default for postgresql is: **postgres**:[none], but, being a responsible dba, you will have changed these.

You should also have an i2b2 client (we use the web client) that can access and query the installed services.

## Quick Summary
The sections below tell you how to:
1) [Load the FHIR Metadata Vocabulary as an i2b2 ontology](#loading-the-FHIR-metadata-vocabulary-into-i2b2)
2) [Load FHIR data as observation facts]()
3) [Run i2b2 queries across FHIR data]()

## Loading the FHIR Metadata Vocabulary into i2b2
There are two ways to load/update an existing set of i2b2 tables:
1) Run `generate_i2b2` and load the tables directly
2) Import the tab separated value (.tsv) tables that have been preloaded as part of this project


### 1. Running `generate_i2b2`

#### Prerequsites 
You need a version of [Python 3](https://www.python.org/) (ideally, 3.6) installed on your computer. 

```text
> python3 --version
Python 3.6.1
>
```

If you are running version 3.5 or earlier, you should consider upgrading.  i2FHIRb2 will <u>not</u> run with Python 2.

#### Download the i2FHIRb2 software 
Download or clone the [FHIR in i2b2 (i2FHIRb2)](https://github.com/BD2KOnFHIR/i2FHIRb2) package into a local directory.
```text
> git clone https://github.com/BD2KonFHIR/i2FHIRb2
> cd i2FHIRb2
```

#### Create a virtual environment
1) Install `virtualenv` if needed:
```text
> virtualenv --version
-bash: virtualenv: command not found    <-- If you get this message ...
> pip install virtualenv                <-- ... install virtualenv
   ...
> virtualenv --version
15.1.0
>
```
2) Create a new virtual environment and activate it
```text
> virtualenv venv -p python3
Running virtualenv with interpreter /Library/Frameworks/Python.framework/Versions/3.6/bin/python3
Using base prefix '/Library/Frameworks/Python.framework/Versions/3.6'
   ...
> . venv/bin/activate
(venv) > 
```

#### Install i2FHIRb2 in the environment

    
In the root project directory (i2FHIRb2):
```text
(venv) > pip install -e .
Obtaining file:///Users/mrf7578/Downloads/i2b2test/i2FHIRb2
Collecting SQLAlchemy (from i2FHIRb2==0.0.2)
Collecting python_dateutil (from i2FHIRb2==0.0.2)
  Using cached python_dateutil-2.6.0-py2.py3-none-any.whl
Collecting rdflib (from i2FHIRb2==0.0.2)
  Using cached rdflib-4.2.2-py3-none-any.whl
   ...
(venv) > 
```
(Don't miss the period  ('.') in the above command)

#### Validate the installation
```text
(venv) > generate_i2b2 -v
Version: 0.1.0              <--- a newer version may print here
```

#### Edit the SQL configuration file 
```text
> cd scripts
> cp db_conf my_conf
> (edit) my_conf
--dburl "postgresql+psycopg2://[[ip]]:[[port]]/i2b2"
--user [[user]]
--password [[password]]
```
(Note that it is also possible to enter the abovecommand line:
```text
(venv) > generate_i2b2 tests/data -l -db "postgresql+psycopg2://localhost:5432/i2b2" -u postgres -p postgres``)
```
 
#### Test the configuration
```text
(venv) > generate_i2b2 -mv ../tests/data/fhir_metadata_vocabulary/ --test @my_conf
Validating input files
	File: ../tests/data/fhir_metadata_vocabulary/fhir.ttl exists
	File: ../tests/data/fhir_metadata_vocabulary/w5.ttl exists
Validating sql connection
	Connection validated
Validating target tables
	Table concept_dimension exists
	Table encounter_mapping exists
	Table modifier_dimension exists
	Table ontology_table exists
	Table patient_dimension exists
	Table patient_mapping exists
	Table provider_dimension exists
	Table table_access exists
	Table visit_dimension exists
Testing write access
	2 rows updated in table_access table
 (venv) > 
```
 
 Further instructions for running the various loader functions can be found in the [scripts](scripts) directory.
 
 
#### Loading the i2b2 ontology tables from the FHIR Metadata Vocabulary
Lines marked with '++' below will only appear the first time the generator is run.</br>
Lines marked with '**' will only appear if the generator has been run previously
The exact numbers will depend on the version of the FMV and/or the loader
```text
(venv) > generate_i2b2 -mv ../tests/data/fhir_metadata_vocabulary/ -l @my_conf
Loading fhir.ttl
loading w5.ttl
** 1 i2b2metadata.table_access record deleted
1 i2b2metadata.table_access record inserted
++ Changing length of concept_dimension.concept_cd from 50 to 200
** 3396 i2b2demodata.concept_dimension records deleted
Recursion on :http://hl7.org/fhir/DomainResource.extension.value.extension http://hl7.org/fhir/Extension
Recursion on :http://hl7.org/fhir/DomainResource.modifierExtension.value.extension http://hl7.org/fhir/Extension
Recursion on :http://hl7.org/fhir/Task.input.value.extension.value http://hl7.org/fhir/Element
Recursion on :http://hl7.org/fhir/Task.output.value.extension.value http://hl7.org/fhir/Element
++ Changing length of modifier_dimension.modifier_cd from 50 to 200
** 2000 i2b2demodata.modifier_dimension records deleted
1861 i2b2demodata.modifier_dimension records inserted
++ Changing length of custom_meta.c_basecode from 50 to 200
++ Changing length of custom_meta.c_tooltip from 700 to 1600
** 10222 i2b2metadata.custom_meta records deleted
** 19 i2b2metadata.custom_meta records deleted
10175 i2b2metadata.custom_meta records inserted
++ 1 i2b2metadata.table_access record inserted
(venv) >
```

### Importing .tsv files

It is also possible to load the i2b2 ontology tables from the set of tab separated value (.tsv) that are included in the
distribution. 

**Note 1:** We do our best to reload these file with each release. Sometimes we don't remember.  Also, the .tsv files
in the distribution are derived from `../tests/data/fhir_metadata_vocabulary`, which may vary slightly from the FMV that
can be found at 'http://build.fhir.org/'.  You can regenerate these tables by:
```text
(venv) > generate_i2b2 -mv ../tests/data/fhir_metadata_vocabulary -l -od ../i2b2files
```

**Note 2:**: Before you load the files below, you may need to adjust the length of the following columns:
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

#### TSV Files
The pre-loaded tsv files can be found in the `i2b2files` subdirectory of the `i2FHIRb2` install:

* **`table_access.tsv`** -- the `table_access` table describes the location and root paths of i2b2 metadata.  This file has one row that states that FHIR resource definitions can be found in the `custom_meta` table with the root '\\FHIR\\'.
* **`concept_dimension.tsv`** --  the `concept_dimension` table links defines the set of possible concept codes that can appear in the `observation_fact` table.  For FHIR, this includes all "first level" resource entries -- Observation.identifier, Observation.basedOn, etc.
* **`modifier_dimension.tsv`** -- the `modifier_dimension` table contains possible modifier codes for the `observation_fact` table.  For FHIR, this contains the substructure represented in the concept codes -- `CodeableConcept.text`, `CodeableConcept.coding`, etc.
* **`ontology.tsv`** -- the "ontology" or "metadata" tables provide a navigational hierarchy that serve to organize and group i2b2 dimensions (`concept`, `modifier`, `patient`, `provider` and `visit`).  The **`i2FHIRb2`** project uses the FHIR W5 tables to provide high level organization and then lists the resources and their possible properties and modifiers for this table.

All of these tables have tab-separated values and the first row of each table has the column headers.   They can be imported directly into the corresponding i2b2 tables

<sub>**NOTE:** We have been unable to convince the postgreSQL import tool to treat empty columns as `NULL` values.  While, in general, the i2b2 software appears to treat NULLs and zero-length strings as equivalent, there is at least one place where this breaks -- the `m_exclusion_cd` column in the `custom_meta` (ontology) table. After loading the `ontology.tsv` table it is necessary to execute the following SQL:
 ```sql
 UPDATE custom_meta SET m_exclusion_cd = NULL WHERE m_exclusion_cd = '';
 ```
</sub>

### Testing the installation
Open the i2b2 browser and navigate to the `FHIR Resources`.  As you drill down it should look like:

![Protege Screenshot](images/SampleBrowser.png)

## Loading FHIR Resource Data
The `loadfacts` program is used to load select FHIR Resource instances in to the i2b2 CRC tables. It requires a number of input parameters:
1) The i2b2 SQL connection information, including the database URL, user name and password.
2) The upload identifier -- an integer that identifies this particular `run`.  It is saved as the `upload_id` in all of the i2b2 CRC tables, allowing you to determine what operation caused the data to be loaded and to undo (via `removefacts`) and reload data if problems are encountered.
3) 


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


