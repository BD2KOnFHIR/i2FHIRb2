# `removefacts` 
`removefacts` is a command line utility for removing i2b2 observation facts that are associated with one or more upload identifiers.

## Usage:
```text
(venv) > removefacts -h
usage: removefacts [-h] [-mv METAVOC] [--conf CONFIG FILE] [-db DBURL]
                   [--user USER] [--password PASSWORD] [--crcdb CRCDB]
                   [--crcuser CRCUSER] [--crcpassword CRCPASSWORD]
                   [--ontodb ONTODB] [--ontouser ONTOUSER]
                   [--ontopassword ONTOPASSWORD]
                   Upload identifiers [Upload identifiers ...]

Clear data from FHIR observation fact table

positional arguments:
  Upload identifiers    Upload identifer(s) -- unique batch identifiers

optional arguments:
  -h, --help            show this help message and exit
  -mv METAVOC, --metavoc METAVOC
                        Metavocabulary directory - ignored
  --conf CONFIG FILE    Configuration file
  -db DBURL, --dburl DBURL
                        Default database URL (default:
                        postgresql+psycopg2://localhost:5432/i2b2)
  --user USER           Default user name (default: postgres)
  --password PASSWORD   Default password (default: postgres)
  --crcdb CRCDB         CRC database URL. (default: dburl)
  --crcuser CRCUSER     User name for CRC database. (default: user)
  --crcpassword CRCPASSWORD
                        Password for CRC database. (default: password
  --ontodb ONTODB       Ontology database URL. (default: dburl)
  --ontouser ONTOUSER   User name for ontology database. (default: user)
  --ontopassword ONTOPASSWORD
                        Password for ontology database. (default: password)
```

## Example
Suppose that you've done two different loads:

```text
(venv) > loadfacts --conf db_conf -l -u 17134
(venv) > loadfacts --conf db_conf -l -u 17135
```
And for some reason, you want to undo the results of this load process.

```text
(venv) > removefacts --conf db_conf 17134 17135
```