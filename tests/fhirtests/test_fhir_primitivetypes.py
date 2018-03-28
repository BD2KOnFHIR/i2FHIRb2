# Copyright (c) 2018, Mayo Clinic
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
from typing import Dict

from fhirtordf.rdfsupport.namespaces import FHIR
from rdflib import Graph, RDFS

from i2fhirb2.fhir.fhirprimitivetypes import i2b2_primitive, I2B2Value
from i2b2model.data.i2b2observationfact import ValueTypeCd

expected: Dict[str, I2B2Value] = {
     'base64': I2B2Value("", ValueTypeCd("B"), None, '"/9j/4AAQS...SgJX2f//Z"'),
     'boolean_false': I2B2Value("false", ValueTypeCd("T"), None, None),
     'boolean_true': I2B2Value("true", ValueTypeCd("T"), None, None),
     'date': I2B2Value("2013-04-01 00:00", ValueTypeCd("D"), 20130401, None),
     'datetime1': I2B2Value("2013-06-20 23:42", ValueTypeCd("D"), 20130620.2342, None),
     'datetime2': I2B2Value("2015-08-06 15:37", ValueTypeCd("D"), 20150806.1537, None),
     'decimal1': I2B2Value("E", ValueTypeCd("N"), 1400.0, None),
     'decimal2': I2B2Value("E", ValueTypeCd("N"), 135.57, None),
     'decimal3': I2B2Value("E", ValueTypeCd("N"), -3.5, None),
     'gyear': I2B2Value("2004-01-01 00:00", ValueTypeCd("D"), 20040101, None),
     'gyearmonth': I2B2Value("2012-06-01 00:00", ValueTypeCd("D"), 20120601, None),
     'integer1': I2B2Value("E", ValueTypeCd("N"), 1001.0, None),
     'integer2': I2B2Value("E", ValueTypeCd("N"), -42.0, None),
     'nonnegint': I2B2Value("E", ValueTypeCd("N"), 6.0, None),
     'positiveint': I2B2Value("E", ValueTypeCd("N"), 3.0, None),
     'time': I2B2Value("16:30:00", ValueTypeCd("D"), 0.163, None)}


class FHIRPrimitiveTypesTestCase(unittest.TestCase):
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

    def test_primitive_types(self):
        g = Graph()
        g.parse(location=os.path.join(self.test_dir, 'primitive_types.ttl'), format="turtle")
        rslts: Dict[str, I2B2Value] = {}
        for o in g.objects(FHIR.Test, FHIR.Passing.values):
            entry_label = g.value(o, RDFS.label).value
            fhir_value = g.value(o, FHIR.value)
            rslts[entry_label] = i2b2_primitive(fhir_value)
        self.assertEqual(expected, rslts)
        

if __name__ == '__main__':
    unittest.main()
