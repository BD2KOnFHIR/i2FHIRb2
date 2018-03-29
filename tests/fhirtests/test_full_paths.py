
import unittest
from typing import List

from rdflib import Graph, RDFS, Namespace, RDF

from i2fhirb2.fhir.fhirontologytable import FHIROntologyTable


EX = Namespace("http://example.org/")


class FullPathTestCase(unittest.TestCase):
    @staticmethod
    def same(l1: List, l2: List) -> bool:
        if len(l1) == len(l2) and all(e in l2 for e in l1):
            return True
        print("list 1: {}".format(', '.join(str(e) for e in l1 if e not in l2)))
        print("list 2: {}".format(', '.join(str(e) for e in l2 if e not in l1)))
        return False

    @unittest.skip
    def test_path(self):
        g = Graph()
        fot = FHIROntologyTable(g)
        #
        self.assertTrue(self.same([[EX.x]], fot.full_paths(EX.x, RDFS.subClassOf)))
        g.add((EX.x, RDF.type, RDFS.Resource))
        # EX.x
        self.assertTrue(self.same([[EX.x]], fot.full_paths(EX.x, RDFS.subClassOf)))
        g.add((EX.x, RDFS.subClassOf, EX.a))
        g.add((EX.x, RDFS.subPropertyOf, EX.z))
        # EX.x --> EX.a
        self.assertTrue(self.same([[EX.a, EX.x]], fot.full_paths(EX.x, RDFS.subClassOf)))
        g.add((EX.a, RDFS.subClassOf, EX.b))
        # EX.x --> EX.a --> EX.b
        self.assertTrue(self.same([[EX.b, EX.a, EX.x]], fot.full_paths(EX.x, RDFS.subClassOf)))
        g.add((EX.x, RDFS.subClassOf, EX.aa))
        # EX.x --> EX.a --> EX.b
        #      --> EX.aa
        self.assertTrue(self.same([[EX.b, EX.a, EX.x],
                                   [EX.aa, EX.x]],
                                  fot.full_paths(EX.x, RDFS.subClassOf)))
        g.add((EX.b, RDFS.subClassOf, EX.c))
        g.add((EX.b, RDFS.subClassOf, EX.e))
        g.add((EX.e, RDFS.subClassOf, EX.f))
        # EX.x --> EX.a --> EX.b --> EX.c
        #                        --> EX.e --> EX.f
        #      --> EX.aa
        self.assertTrue(self.same([[EX.c, EX.b, EX.a, EX.x],
                                   [EX.f, EX.e, EX.b, EX.a, EX.x],
                                   [EX.aa, EX.x]],
                                  fot.full_paths(EX.x, RDFS.subClassOf)))

        self.assertTrue(self.same(['\\A\\c\\b\\a\\', '\\A\\f\\e\\b\\a\\', '\\A\\aa\\'],
                                  fot.i2b2_paths('\\A\\', EX.x, RDFS.subClassOf)))

        self.assertTrue(self.same(['\\A\\aa\\'],
                                  fot.i2b2_paths('\\A\\', EX.x, RDFS.subClassOf, lambda l: EX.b not in l)))


if __name__ == '__main__':
    unittest.main()
