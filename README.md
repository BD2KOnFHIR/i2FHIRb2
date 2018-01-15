# i2FHIRb2 - FHIR in i2b2

## Edit history
* 0.2.0 - Major overhaul
* 0.2.1 - `Observation.referenceRange` temporarily removed to allow batch loads

## Introduction
This package creates an i2b2 ontology from the FHIR STU3/R4 resource model.  It uses a combination of the [FHIR W5 (who, what, why, where, when) ontology](http://build.fhir.org/w5.ttl) and the [FHIR Resource Ontology](http://build.fhir.org/fhir.ttl) to create an i2b2 equivalent.

    
## I2B2 requirements
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
You need a current version of [Python 3](https://www.python.org/) (>= 3.6) installed on your computer.  ()At some point we may be able to back-rev this to earlier Python 3 versions, but, for not...)

```text
> python3 --version
Python 3.6.1
>
```

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
Collecting SQLAlchemy (from i2FHIRb2==0.1.0)
Collecting python_dateutil (from i2FHIRb2==0.1.0)
  Using cached python_dateutil-2.6.1-py2.py3-none-any.whl
Collecting rdflib (from i2FHIRb2==0.1.0)
  Using cached rdflib-4.2.2-py3-none-any.whl
   ...
(venv) > 
```
(Don't miss the period  ('.') in the above command)

#### Validate the installation
```text
(venv) > generate_i2b2 -v
Version: 0.2.0              <--- a newer version may print here
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
Note that it is also possible to enter the above as a command line:
```text
(venv) > generate_i2b2 -l --dburl "postgresql+psycopg2://localhost:5432/i2b2" --user postgres --password postgres ...
```
 
#### Test the configuration
```text
(venv) > generate_i2b2 --conf my_conf --test
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
(venv) > generate_i2b2 --conf my_conf -l
Loading fhir.ttl
 (cached)
loading w5.ttl
 done

1 i2b2metadata.table_access record deleted
1 i2b2metadata.table_access record inserted
4388 i2b2demodata.concept_dimension records deleted
2158 i2b2demodata.concept_dimension records inserted
2231 i2b2demodata.modifier_dimension records deleted
743 i2b2demodata.modifier_dimension records inserted
13588 i2b2metadata.custom_meta records deleted
19 i2b2metadata.custom_meta records deleted
15255 i2b2metadata.custom_meta records inserted
(venv) >
```

### Importing .tsv files

It is also possible to load the i2b2 ontology tables from the set of tab separated value (.tsv) that are included in the
distribution. 

**Note 1:** We do our best to reload these file with each release. Sometimes we don't remember.  Also, the .tsv files
in the distribution are derived from `../tests/data/fhir_metadata_vocabulary`, which may vary slightly from the FMV that
can be found at 'http://build.fhir.org/'.  You can regenerate these tables by:
```text
(venv) > generate_i2b2 --conf my_conf -od ../i2b2files
Loading fhir.ttl
 (cached)
loading w5.ttl
 done

writing ../i2b2files/table_access.tsv (1) records written
writing ../i2b2files/concept_dimension.tsv (2158) records written
writing ../i2b2files/modifier_dimension.tsv (743) records written
writing ../i2b2files/ontology_table.tsv (15255) records written
(venv) >
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

**NOTE:** We have been unable to convince the postgreSQL import tool to treat empty columns as `NULL` values.  While, in general, the i2b2 software appears to treat NULLs and zero-length strings as equivalent, there is at least one place where this breaks -- the `m_exclusion_cd` column in the `custom_meta` (ontology) table. After loading the `ontology.tsv` table it is necessary to execute the following SQL:
 ```sql
 UPDATE custom_meta SET m_exclusion_cd = NULL WHERE m_exclusion_cd = '';
 ```


### Testing the installation
Open the i2b2 browser and navigate to the `FHIR Resources`.  As you drill down it should look like:

<img src="images/SampleBrowser.png" width="300">

![webclient screenshot](images/SampleBrowser.png)

## Loading FHIR Resource Data
The `loadfacts` program is used to load select FHIR Resource instances in to the i2b2 CRC tables. It can load data from a list of files, a list of URLs or an input directory.  Input can either be in JSON or Turtle format. Both an `upload_id` and `sourcesystem_cd` can be specified
for tracking and management purposes.

### Example
```text
(venv) > loadfacts -v
FHIR i2b2 CRC loader -- Version 0.2.0
(venv) > loadfacts --conf db_conf -u 117 --sourcesystem "FHIR R4" -l -t json --dupcheck -rm -i http://build.fhir.org/observation-example-f001-glucose.json
upload_id: 117
  Starting encounter number: 527091
  Starting patient number: 1000000213
--> loading http://build.fhir.org/observation-example-f001-glucose.json
89 triples
0: (Patient) - http://hl7.org/fhir/Patient/f001
1: (Observation) - http://hl7.org/fhir/Observation/f001
2: (Practitioner) - http://hl7.org/fhir/Practitioner/f005
---> Graph map phase complete
Generated:
    30 Observation facts
    1 Patients
    2 Patient mappings
=== SKIPS ===
    0 Bundled resources (shouldn't happen?)
    0 Visit resources
    0 Infrastructure resources
    0 Provider resources
    1 Unmapped resources

Deleted 3 patient_dimension records
Deleted 4 patient_mapping records
Deleted 26 observation_fact records
Deleted 3 visit_dimension records
Deleted 4 encounter_mapping records
1 / 0 patient_dimension records added / modified
2 / 0 patient_mapping records added / modified
1 / 0 visit_dimension records added / modified
2 / 0 encounter_mapping records added / modified
4 duplicate records encountered
Key: (1000000213, 'FHIR:Observation.referenceRange', 'FHIR:Quantity.value', datetime.datetime(2017, 12, 21, 11, 13, 6, 736196), 527091, 3, 'FHIR:DefaultProvider') has a non-identical dup
26 / 0 observation_fact records added / modified
(venv) >
```
The above example uses the following parameters:
* **`--conf my_conf`**  db connection and fhirt.ttl link
* **`-u 117`** upload identifier
* **`--sourcesystem "FHIR R4"`** sourcesystem_cd
* **`-l`** load the data tables
* **`-t json`** source format is JSON
* **`--dupcheck`** Check for duplicate records before loading. Needed to address some unresolved issues in reference range representation.
* **`-rm`** Remove existing entries for this upload id before loading (Useful for testing)
* **`-i http://build.fhir.org/observation-example-f001-glucose.json` Input comes from this URL


The results of the above load can be (indirectly) viewed with a query such as the one below:
![sample query](images/QuerySample.png)

Note that `Selected groups occur in the same financial encounter` is selected in the "temporal constraint".  We are currently using the notion of "encounter" to represent "resource" -- the selection says that the code, the system and the interpretation all have to occur on the same encounter.

The results for this query (we selected the "Patient Set", "Encounter Set" and "Number of Patients" options) are shown below:

![sample query output](images/QuerySampleResult.png)

We can add patient demographics by following the link in the observation, loading:
```text
(venv) > loadfacts --conf db_conf -u 117 --sourcesystem "FHIR R4" -l -t json --dupcheck -i http://hl7.org/fhir/patient-example-f001-pieter.json
upload_id: 117
  Starting encounter number: 527092
  Starting patient number: 1000000214
--> loading http://hl7.org/fhir/patient-example-f001-pieter.json
136 triples
0: (Organization) - http://hl7.org/fhir/Organization/f001
1: (Patient) - http://hl7.org/fhir/Patient/f001
---> Graph map phase complete
Generated:
    0 Observation facts
    1 Patients
    2 Patient mappings
=== SKIPS ===
    0 Bundled resources (shouldn't happen?)
    0 Visit resources
    0 Infrastructure resources
    1 Provider resources
    0 Unmapped resources

1 / 0 patient_dimension records added / modified
1 / 1 patient_mapping records added / modified
0 / 0 visit_dimension records added / modified
0 / 0 encounter_mapping records added / modified
0 / 0 observation_fact records added / modified
(venv) >
```



## Current State of the Project
At the moment, the FHIR structural model is represented pretty much verbatim in the i2b2 ontology and the corresponding resources instances in the i2b2 observation_fact table. We have demonstrated that it is possible to create queries in the i2b2 web client to access this information, but it should also be obvious that these queries would be unapproachable to anyone who wasn't both a FHIR and i2b2 model expert.

The next steps include:
### Mapping  [FHIR data types](http://www.hl7.org/FHIR/datatypes.html) to i2b2 equivalents.
Currently, FHIR data types are represented quite literally.  As an example [FHIR Quantity](http://www.hl7.org/FHIR/datatypes.html#quantity) currently has a separate row for `Quantity.unit`,
`Quantity.code`, `Quantity.comparator`, `Quantity.value` and `Quantity.system`.  There is a close correspondence between these and the observation_fact value columns `units_cd`, `tval_char`, and `nval_num` entries.  In addition, the `valueflag_cd` has a close correspondence to the [FHIR Observation interpretation](http://www.hl7.org/FHIR/observation-definitions.html#Observation.interpretation) field

### Representing FHIR coded concepts as i2b2 concept codes.
Currently, the [FHIR code](http://www.hl7.org/FHIR/datatypes.html#code), [FHIR Coding](http://www.hl7.org/FHIR/datatypes.html#Coding) and [FHIR CodeableConcept](http://www.hl7.org/FHIR/datatypes.html#CodeableConcept) data element values are represented as textual values.  We need to create i2b2 concept and/or modifier codes that represent this information.  This step would provide a key entry point to the use of FHIR terminologies in the i2b2 space.

### Adapt i2b2 value widgets to the FHIR use case

### Connect to FHIR terminologies and (possibly) terminology servers
 
### Representing FHIR resources as first class groupings.
Currently, we have preempted the "visit/financial encounter" dimension to represent FHIR resources.  We need to extend the i2b2 model to be able to group elements on the "Observation" or "Resource" level.
       
### Patient and Provide dimensions
The project currently assumes that all information appears in the `observation_fact` table.  This obviously isn't the case as:
* Patient / provider / visit information either maps to or extends the i2b2 dimension tables
* Resources such as 'Device', 'Medication', etc. currently have no place in i2b2 at all.
