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
import unittest

import sys
from rdflib import Graph

from i2fhirb2.rdfsupport.rdfcompare import rdf_compare

# If true, we're updating the target. Will always return a fail
save_output = False


class JSONToRDFTestCase(unittest.TestCase):

    def test_patient_dimension(self):
        from i2fhirb2.jsontordf import jsontordf

        test_directory = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'data')
        infile = os.path.join(test_directory, "patient-example.json")
        rdf = jsontordf([infile])
        testfname = os.path.join(test_directory, "patient-example.ttl")

        if save_output:
            with open(testfname, "w") as outf:
                outf.write(str(rdf))
            print("---> RDF written to {}".format(testfname))
            self.assertTrue(False, "Generating a new test file")

        target = Graph()
        target.load(testfname, format="turtle")
        self.assertTrue(rdf_compare(target, rdf.graph, sys.stdout))

if __name__ == '__main__':
    unittest.main()
