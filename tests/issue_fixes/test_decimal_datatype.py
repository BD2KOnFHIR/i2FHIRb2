
import unittest

from rdflib import Literal, XSD


class DecimalDatatypeTestCase(unittest.TestCase):
    def test_decimal_literal(self):
        self.assertNotEqual(str(Literal("117.50", datatype=XSD.decimal)),
                            str(Literal("117.5", datatype=XSD.decimal)))
        self.assertEqual(Literal(117.50),
                         Literal(117.5))
        self.assertEqual(Literal(117.50, datatype=XSD.decimal),
                         Literal(117.5, datatype=XSD.decimal))
        self.assertNotEqual(Literal("117.50", datatype=XSD.decimal),
                            Literal("117.5", datatype=XSD.decimal))
        self.assertEqual(Literal("117.50", datatype=XSD.decimal).toPython(),
                         Literal("117.5", datatype=XSD.decimal).toPython())


if __name__ == '__main__':
    unittest.main()
