# i2FHIRb2 - FHIR in i2b2

## Introduction
This package creates an i2b2 ontology from the FHIR STU3/R4 resource model.  It uses a combination of the [FHIR W5 (who, what, why, where, when) ontology](http://build.fhir.org/w5.ttl) and the [FHIR Resource Ontology](http://build.fhir.org/fhir.ttl) to create an i2b2 equivalent.

## Installation
1) Clone or download this package from [https://github.com/BD2KOnFHIR/i2FHIRb2](https://github.com/BD2KOnFHIR/i2FHIRb2)
   ```bash
   > git clone https://github.com/BD2KOnFHIR/i2FHIRb2
   > cd i2FHIRb2
    ```
    
## Loading i2b2 tables
There are two ways to load/update an existing set of i2b2 tables:
1) Run `generate_i2b2` and load the tables directly
2) Import the tab separated value (.tsv) tables that have been preloaded as part of this project

### Running `generate_i2b2`

#### Prerequsites 
You need a version of [Python 3](https://www.python.org/) (ideally, 3.6) installed on your computer. 

```text
> python3 --version
Python 3.6.1
>
```

 
1) Download or clone the [FHIR in i2b2 (i2FHIRb2)](https://github.com/BD2KOnFHIR/i2FHIRb2) package.
```text
> git clone https://github.com/BD2KonFHIR/i2FHIRb2
> cd i2FHIRb2
```

2) (Optional) Create a virtual environment:
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
    2) Activate the virtual environment
    ```text
    > virtualenv venv -p python3
    Running virtualenv with interpreter /Library/Frameworks/Python.framework/Versions/3.6/bin/python3
    Using base prefix '/Library/Frameworks/Python.framework/Versions/3.6'
       ...
    > . venv/bin/activate
    (venv) > 
    ```
3) Install dependencies, etc. 
    
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
   ```
   (Don't miss the '.' in the above command)
   
   i2FHIRb2 comes with the python postgresql driver (psycopg2) pre-installed. If you are using an Oracle databae, you need to:
   ```text
    (venv) > pip install cx_Oracle --pre       
       ...
    (venv) > 
    ```
    (Note: these tools haven't been tested with Oracle -- they may not work)
    
    There are a number of different dialects available for Microsoft SQL Server. See: http://docs.sqlalchemy.org/en/latest/dialects/mssql.html for details. Note that the same testing caveat applies.
4) Validate the installation
    ```bash
    (venv) > generate_i2b2 -h
     usage: generate_i2b2 [-h] [-o OUTDIR] [-t TABLE] [-r RESOURCE]
                     [--sourcesystem SOURCESYSTEM_CD] [--base BASE] [-l] [-g]
                     [-v] [--list] [-db DBURL] [-u USER] [-p PASSWORD]
                     [--test] [--crcdb CRCDB] [--crcuser CRCUSER]
                     [--crcpassword CRCPASSWORD] [--ontdb ONTDB]
                     [--ontuser ONTUSER] [--ontpassword ONTPASSWORD]
                     [--onttable ONTTABLE]
                     indir

    FHIR in i2b2 metadata generator
    
    positional arguments:
      indir                 Input directory or URI of w5.ttl and fhir.ttl files
    
    optional arguments:
      -h, --help            show this help message and exit
      -o OUTDIR, --outdir OUTDIR
                            Output directory to store .tsv files. If absent, .tsv
                            files are not generated.
      -t TABLE, --table TABLE
                            Table to update (concept_dimension,
                            modifier_dimension, ontology_table, table_access)
                            (default: All tables)
      -r RESOURCE, --resource RESOURCE
                            Name of specific resource to emit (e.g. Observation).
                            (default: all)
      --sourcesystem SOURCESYSTEM_CD
                            sourcesystem code (default: "FHIR STU3")
      --base BASE           Concept dimension base path. (default: "\FHIR\")
      -l, --load            Load i2b2 SQL tables
      -g, --gentsv          Generate TSV output
      -v, --version         show program's version number and exit
      --list                List table names
      -db DBURL, --dburl DBURL
                            Default database URL
      -u USER, --user USER  Default user name
      -p PASSWORD, --password PASSWORD
                            Default password
      --test                Test the confguration
      --crcdb CRCDB         CRC database URL. (default: DBURL)
      --crcuser CRCUSER     User name for CRC database. (default: USER)
      --crcpassword CRCPASSWORD
                            Password for CRC database. (default: PASSWORD
      --ontdb ONTDB         Ontology database URL. (default: DBURL)
      --ontuser ONTUSER     User name for ontology database. (default: USER)
      --ontpassword ONTPASSWORD
                            Password for ontology database. (default: PASSWORD
      --onttable ONTTABLE   Ontology table name (default: custom_meta)
   ```
5) Edit the SQL configuration file.
      
   Edit db_conf config file and change the db, user and password parameters. In the i2FHIRb2 root directory:
 
    ```text
    > cd scripts
    > edit db_conf
    -db "postgresql+psycopg2://localhost:5432/i2b2"
    --user postgres
    --password postgres
    ```
    (Note that these parameters can also be run directly from the command line:
    ```text
    (venv) > generate_i2b2 tests/data -l -db "postgresql+psycopg2://localhost:5432/i2b2" -u postgres -p postgres``)
 
6) Test the configuration:
    ```text
    (venv) > generate_i2b2 tests/data --test @db.conf
     Validating input files
        File: ../tests/data/fhir.ttl exists
        File: ../tests/data/w5.ttl exists
    Validating sql connection
        Connection validated
    Validating target tables
        Table concept_dimension exists
        Table modifier_dimension exists
        Table ontology_table exists
        Table patient_dimension exists
        Table provider_dimension exists
        Table table_access exists
        Table visit_dimension exists
    Testing write access
        2 rows updated in table_access table
     (venv) >
        
    ```
   
6) Run the FHIR in i2b2 loader

```text
(venv) > generate_i2b2 tests/data -l @db_conf
Loading fhir.ttl
loading w5.ttl
1 i2b2metadata.table_access record inserted
Changing length of concept_dimension.concept_cd from 50 to 200
1466 i2b2demodata.concept_dimension records inserted
Changing length of modifier_dimension.modifier_cd from 50 to 200
6629 i2b2demodata.modifier_dimension records inserted
Changing length of custom_meta.c_basecode from 50 to 200
Changing length of custom_meta.c_tooltip from 700 to 1600
10016 i2b2metadata.custom_meta records inserted
(venv) >
```

### Importing .tsv files


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

## Testing the installation
Open the i2b2 browser and navigate to the `FHIR Resources`.  As you drill down it should look like:

![Protege Screenshot](images/SampleBrowser.png)


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


