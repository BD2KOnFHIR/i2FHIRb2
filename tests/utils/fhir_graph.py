import os

from fhirtordf.fhir.fhirmetavoc import FHIRMetaVoc

test_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
test_conf_directory = os.path.join(test_directory, 'conf')
test_conf_file = os.path.abspath(os.path.join(test_conf_directory, 'db_conf'))
test_data_directory = os.path.join(test_directory, 'data')

mvdir = os.path.abspath(os.path.join(test_data_directory, 'fhir_metadata_vocabulary'))


def FHIRGraph():
    print("Loading graph", end="")
    fmv = FHIRMetaVoc(os.path.join(mvdir, 'fhir.ttl'))
    print(" (cached)" if fmv.from_cache else "(from disc)", end="")
    fmv.g.load(os.path.join(mvdir, 'w5.ttl'), format="turtle")
    print(" done\n")
    return fmv.g
