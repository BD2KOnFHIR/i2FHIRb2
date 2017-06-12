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

import unittest
from typing import List

from rdflib import Graph, RDFS, Namespace, RDF

from i2fhirb2.fhir.fhirspecific import full_paths, i2b2_paths, nsmap

EX = Namespace("http://example.org/")
nsmap[str(EX)] = "EX"


class FullPathTestCase(unittest.TestCase):
    @staticmethod
    def same(l1: List, l2: List) -> bool:
        if len(l1) == len(l2) and all(e in l2 for e in l1):
            return True
        print("list 1: {}".format(', '.join(str(e) for e in l1 if e not in l2)))
        print("list 2: {}".format(', '.join(str(e) for e in l2 if e not in l1)))
        return False

    def test_path(self):
        g = Graph()
        #
        self.assertTrue(self.same([[EX.x]], full_paths(g, EX.x, RDFS.subClassOf)))
        g.add((EX.x, RDF.type, RDFS.Resource))
        # EX.x
        self.assertTrue(self.same([[EX.x]], full_paths(g, EX.x, RDFS.subClassOf)))
        g.add((EX.x, RDFS.subClassOf, EX.a))
        g.add((EX.x, RDFS.subPropertyOf, EX.z))
        # EX.x --> EX.a
        self.assertTrue(self.same([[EX.a, EX.x]], full_paths(g, EX.x, RDFS.subClassOf)))
        g.add((EX.a, RDFS.subClassOf, EX.b))
        # EX.x --> EX.a --> EX.b
        self.assertTrue(self.same([[EX.b, EX.a, EX.x]], full_paths(g, EX.x, RDFS.subClassOf)))
        g.add((EX.x, RDFS.subClassOf, EX.aa))
        # EX.x --> EX.a --> EX.b
        #      --> EX.aa
        self.assertTrue(self.same([[EX.b, EX.a, EX.x],
                                   [EX.aa, EX.x]],
                                  full_paths(g, EX.x, RDFS.subClassOf)))
        g.add((EX.b, RDFS.subClassOf, EX.c))
        g.add((EX.b, RDFS.subClassOf, EX.e))
        g.add((EX.e, RDFS.subClassOf, EX.f))
        # EX.x --> EX.a --> EX.b --> EX.c
        #                        --> EX.e --> EX.f
        #      --> EX.aa
        self.assertTrue(self.same([[EX.c, EX.b, EX.a, EX.x],
                                   [EX.f, EX.e, EX.b, EX.a, EX.x],
                                   [EX.aa, EX.x]],
                                  full_paths(g, EX.x, RDFS.subClassOf)))

        self.assertTrue(self.same(['\\A\\c\\b\\a\\', '\\A\\f\\e\\b\\a\\', '\\A\\aa\\'],
                                  i2b2_paths('\\A\\', g, EX.x, RDFS.subClassOf)))

        self.assertTrue(self.same(['\\A\\aa\\'],
                                  i2b2_paths('\\A\\', g, EX.x, RDFS.subClassOf, lambda l: EX.b not in l)))


if __name__ == '__main__':
    unittest.main()
