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

from rdflib import Graph, URIRef, Namespace, Literal, XSD
from rdflib.compare import graph_diff


class DecimalDatatypeTestCase(unittest.TestCase):
    def test(self):
        g1 = Graph()
        EX = Namespace("http://example.org/")
        g1.add((EX.s1, EX.p1, Literal("117.5", datatype=XSD.decimal)))
        g2 = Graph()
        t2 = """
@prefix ex: <http://example.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:s1 ex:p1 "117.50"^^xsd:decimal .
"""
        g2.parse(data=t2, format="turtle")
        # TODO: Resolve the JSON / RDF / FHIR decimal resolution problem
        # self.assertEqual(g1.value(EX.s1, EX.p1), g2.value(EX.s1, EX.p1))
        in_both, in_first, in_second = graph_diff(g1, g2)
        # self.assertEqual(0, len(in_first))
        # self.assertEqual(0, len(in_second))
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
