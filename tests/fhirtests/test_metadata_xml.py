
import unittest
from datetime import datetime

from i2fhirb2.fhir.fhirspecific import FHIR


class MetadataXMLTestCase(unittest.TestCase):

    def test_basics(self):
        from i2fhirb2.fhir.fhirdimensionmetadata import metadata_xml
        rval = metadata_xml(FHIR.string, "FHIR:Text.string", "Text value", datetime(2017, 7, 31))
        self.assertEqual("""<?xml version="1.0"?>
<ValueMetadata>
    <Version>3.02</Version>
    <CreationDateTime>2017-07-31 00:00:00</CreationDateTime>
    <TestID>FHIR:Text.string</TestID>
    <TestName>Text value</TestName>
    <DataType>String</DataType>
    <Flagstouse/>
    <Oktousevalues>Y</Oktousevalues>
    <EnumValues></EnumValues>
    <UnitValues/>
</ValueMetadata>""", rval)
        self.assertIsNone(metadata_xml(FHIR.root, "FHIR:Text.string", "Text value", datetime(2017, 7, 31)))
        self.assertIsNone(metadata_xml(FHIR.foo, "FHIR:something", "Something not good", datetime(2017, 7, 31)))

        self.assertEqual("""<?xml version="1.0"?>
<ValueMetadata>
    <Version>3.02</Version>
    <CreationDateTime>2017-07-31 00:00:00</CreationDateTime>
    <TestID>FHIR:Like.boolean</TestID>
    <TestName>Do you like me</TestName>
    <DataType>Enum</DataType>
    <Flagstouse/>
    <Oktousevalues>Y</Oktousevalues>
    <EnumValues>
        <Val description="True value">True</Val>
        <Val description="False value">False</Val>
    </EnumValues>
    <UnitValues/>
</ValueMetadata>""", metadata_xml(FHIR.boolean, "FHIR:Like.boolean", "Do you like me", datetime(2017, 7, 31)))
        # TODO: change the type back to FHIR.code when we fully implement FHIR.code
        rval = metadata_xml(FHIR.realcode, "FHIR:Coded.realcode", "Flavors", datetime(2017, 7, 31),
                            [("Blue", "B"), ("Yeller", "Y"), ("Squeak", "SQK")])
        self.assertEqual("""<?xml version="1.0"?>
<ValueMetadata>
    <Version>3.02</Version>
    <CreationDateTime>2017-07-31 00:00:00</CreationDateTime>
    <TestID>FHIR:Coded.realcode</TestID>
    <TestName>Flavors</TestName>
    <DataType>Enum</DataType>
    <Flagstouse/>
    <Oktousevalues>Y</Oktousevalues>
    <EnumValues>
        <Val description="Blue">B</Val>
        <Val description="Yeller">Y</Val>
        <Val description="Squeak">SQK</Val>
    </EnumValues>
    <UnitValues/>
</ValueMetadata>""", rval)


if __name__ == '__main__':
    unittest.main()
