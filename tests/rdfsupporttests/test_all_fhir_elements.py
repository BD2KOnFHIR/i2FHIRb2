# Copyright (c) 2017, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the Mayo Clinic nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import os
import sys
import unittest

from rdflib import Graph

from i2fhirb2.loaders.fhirmetavoc import FHIRMetaVoc
from i2fhirb2.loaders.fhirresourceloader import FHIRResource
from i2fhirb2.rdfsupport.prettygraph import PrettyGraph
from i2fhirb2.rdfsupport.rdfcompare import rdf_compare
from tests.rdfsupporttests.build_test_harness import ValidationTestCase
from tests.utils.base_test_case import FHIRGraph, test_output_directory, test_data_directory


class FHIRInstanceTestCase(ValidationTestCase):
    @classmethod
    def setUpClass(cls):
        cls.fhir_ontology = FHIRGraph()

FHIRInstanceTestCase.input_directory = "/Users/mrf7578/Development/fhir/build/publish"
FHIRInstanceTestCase.file_suffix = ".json"
FHIRInstanceTestCase.skip = ['valuesets.json', 'xds-example.json']
FHIRInstanceTestCase.file_filter = lambda dp, fn: ".cs." not in fn and '.vs.' not in fn and '.profile.' not in fn \
                                                  and '.canonical' not in fn and '/v2/' not in dp and '/v3/' not in dp \
                                                  and '.schema.' not in fn and '.diff.' not in fn
FHIRInstanceTestCase.base_dir = 'http://hl7.org/fhir'
FHIRInstanceTestCase.start_at = "claim-example-oral-bridge"
FHIRInstanceTestCase.single_file = True

# Comparing to FHIR, so make certain we're doing FHIR dates
FHIRMetaVoc.fhir_dates = True


def json_to_ttl(self: FHIRInstanceTestCase, dirpath: str, fname: str) -> bool:
    json_file = os.path.join(dirpath, fname)
    turtle_fname = fname.rsplit('.', 1)[0] + '.ttl'
    source = FHIRResource(self.fhir_ontology, json_file, FHIRInstanceTestCase.base_dir)
    test_ttl_fname = os.path.join(dirpath, turtle_fname)
    if os.path.exists(test_ttl_fname):
        target = Graph()
        target.load(test_ttl_fname, format="turtle")
        if not rdf_compare(source.graph, target, sys.stdout, ignore_owl_version=True, ignore_type_arcs=True):
            with open(os.path.join(test_output_directory, turtle_fname), 'w') as f:
                f.write(str(source))
            return False
        return True
    else:
        print("===> {} does not exist!".format(test_ttl_fname))
        return True


FHIRInstanceTestCase.validation_function = json_to_ttl
FHIRInstanceTestCase.build_test_harness()


if __name__ == '__main__':
    unittest.main()
