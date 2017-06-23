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

import re
import unittest

from i2fhirb2.fhir.fhirspecific import FHIR


class MetadataXMLTestCase(unittest.TestCase):
    @staticmethod
    def fix_date(xml_txt: str) -> str:
        return re.sub(r'<CreationDateTime>.*</CreationDateTime>',
                      '<CreationDateTime>---</CreationDateTime>', xml_txt)

    def test_basics(self):
        from i2fhirb2.i2b2model.metadata_xml import metadata_xml
        rval = metadata_xml(FHIR.string, "FHIR:Text.string", "Text value")
        self.assertEqual("""<?xml version="1.0"?>
<ValueMetadata>
    <Version>3.02</Version>
    <CreationDateTime>---</CreationDateTime>
    <TestID>FHIR:Text.string</TestID>
    <TestName>Text value</TestName>
    <DataType>String</DataType>
    <Flagstouse/>
    <Oktousevalues>Y</Oktousevalues>
    <EnumValues></EnumValues>
    <UnitValues/>
</ValueMetadata>""", self.fix_date(rval))
        self.assertIsNone(metadata_xml(FHIR.root, "FHIR:Text.string", "Text value"))
        self.assertIsNone(metadata_xml(FHIR.foo, "FHIR:something", "Something not good"))

        self.assertEqual("""<?xml version="1.0"?>
<ValueMetadata>
    <Version>3.02</Version>
    <CreationDateTime>---</CreationDateTime>
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
</ValueMetadata>""", self.fix_date(metadata_xml(FHIR.boolean, "FHIR:Like.boolean", "Do you like me")))

        rval = metadata_xml(FHIR.code, "FHIR:Coded.code", "Flavors",
                            [("Blue", "B"), ("Yeller", "Y"), ("Squeak", "SQK")])
        self.assertEqual("""<?xml version="1.0"?>
<ValueMetadata>
    <Version>3.02</Version>
    <CreationDateTime>---</CreationDateTime>
    <TestID>FHIR:Coded.code</TestID>
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
</ValueMetadata>""", self.fix_date(rval))


if __name__ == '__main__':
    unittest.main()
