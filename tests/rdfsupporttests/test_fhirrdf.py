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

from jsonasobj import load

from i2fhirb2.rdfsupport.prettygraph import PrettyGraph
from i2fhirb2.rdfsupport.rdfcompare import rdf_compare
from tests.utils.base_test_case import test_data_directory, test_output_directory


class FhirDataLoaderTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tests.utils.base_test_case import FHIRGraph
        cls.fhir_ontology = FHIRGraph()

    def test_baseuri(self):
        from i2fhirb2.loaders.fhirresourceloader import FHIRResource
        self.assertEqual("http://hl7.org/fhir/",
                         FHIRResource.base_uri("http://hl7.org/fhir/Account/example", "example", "Account"))
        self.assertEqual("http://hl7.org/fhir/",
                         FHIRResource.base_uri("http://hl7.org/fhir/Account#example", "example", "Account"))
        self.assertEqual("http://hl7.org/fhir/",
                         FHIRResource.base_uri("http://hl7.org/fhir/Account/example/test#1", "example/test#1", "Account"))
        self.assertEqual("http://hl7.org/fhir/",
                         FHIRResource.base_uri("http://hl7.org/fhir/Account#example", None, "Account"))
        self.assertEqual("http://hl7.org/fhir/",
                         FHIRResource.base_uri("http://hl7.org/fhir/Account/example", None, "Account"))
        self.assertIsNone(FHIRResource.base_uri("http://hl7.org/fhir/Account#example", "test", "Account"))
        self.assertIsNone(FHIRResource.base_uri("http://hl7.org/fhir/Account#example", "example", "Claim"))
        self.assertIsNone(FHIRResource.base_uri("http://hl7.org/fhir/Account#example", "example", "Account/"))
        self.assertIsNone(FHIRResource.base_uri("http://hl7.org/fhir/Account#example", "example", "/Account"))
        self.assertIsNone(FHIRResource.base_uri("http://hl7.org/fhir/Account#example", "example", "AnAccount"))
        self.assertIsNone(FHIRResource.base_uri("http://hl7.org/fhir/Account#example", "example/", "Account"))
        self.assertIsNone(FHIRResource.base_uri("http://hl7.org/fhir/Account#example", "/example", "Account"))
        self.assertIsNone(FHIRResource.base_uri("http://hl7.org/fhir/Account#example", None, "Claim"))

    def do_test(self, fname, root):
        from i2fhirb2.loaders.fhirresourceloader import FHIRResource

        json_file = fname + ".json"
        turtle_file = fname + ".ttl"
        source = FHIRResource(self.fhir_ontology, os.path.join(test_data_directory, json_file), root)
        with open(os.path.join(test_output_directory, turtle_file), 'w') as output:
            output.write(str(source))
        target = PrettyGraph()
        target.load(os.path.join(test_data_directory, turtle_file), format="turtle")
        self.assertTrue(rdf_compare(source.graph, target, sys.stdout, ignore_owl_version=False))

    def test_observation_example_bmd(self):
        self.do_test('observation-example-bmd', "http://hl7.org/fhir/")

    def test_account_example(self):
        # Note: trailing slash deliberately omitted to test FHIRResource constructor
        self.do_test('account-example', 'http://hl7.org/fhir')

    def test_observation_example_f001_glucose(self):
        self.do_test('observation-example-f001-glucose', "http://hl7.org/fhir/")

    def test_data_entry(self):
        from i2fhirb2.loaders.fhirresourceloader import FHIRResource
        with open(os.path.join(test_data_directory, 'synthea_data', 'fhir', 'Adams301_Keyshawn30_74.json')) as f:
            collection = load(f)
        source = FHIRResource(self.fhir_ontology, None, "http://standardhealthrecord.org/fhir/", data=collection.entry[0].resource)
        with open(os.path.join(test_output_directory, 'synthea_data', 'fhir', 'Adams301_Keyshawn30_74_entry0.ttl'), 'w') as output:
            output.write(str(source))
        # target = PrettyGraph()
        # target.load(os.path.join(test_data_directory, turtle_file), format="turtle")
        # self.assertTrue(rdf_compare(source.graph, target, sys.stdout, ignore_header=False))
        self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
