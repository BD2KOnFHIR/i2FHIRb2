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
from collections import OrderedDict
from datetime import datetime

from rdflib import Graph

from i2fhirb2.fhir.fhirmodifierdimension import FHIRModifierDimension
from i2fhirb2.fhir.fhirspecific import W5, FHIR
from i2fhirb2.i2b2model.i2b2modifierdimension import ModifierDimension
from tests.base_test_case import BaseTestCase, shared_graph


class ModifierDimensionTestCase(BaseTestCase):
    dirname, _ = os.path.split(os.path.abspath(__file__))
    g = Graph()

    @classmethod
    def setUpClass(cls):
        cls.g.load(os.path.join(cls.dirname, 'data', 'w5.ttl'), format="turtle")
        cls.g.load(os.path.join(cls.dirname, 'data', 'fhir.ttl'), format="turtle")

    def test_basics(self):
        from i2fhirb2.i2b2model.i2b2modifierdimension import ModifierDimension
        ModifierDimension._clear()
        ModifierDimension.graph = self.g
        ModifierDimension.download_date = datetime(2017, 5, 25)
        ModifierDimension.sourcesystem_cd = "FHIR"
        ModifierDimension.import_date = datetime(2017, 5, 25)
        md = ModifierDimension(W5["cause"], "\\FHIR\\w5\\who\\")
        self.assertAlmostNow(md.update_date)
        ModifierDimension.update_date = datetime(2001, 12, 1)
        expected = OrderedDict([
             ('modifier_path', '\\FHIR\\w5\\who\\cause\\'),
             ('modifier_cd', 'W5:cause'),
             ('name_char', 'W5 cause'),
             ('modifier_blob', ''),
             ('update_date', datetime(2001, 12, 1, 0, 0)),
             ('download_date', datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', None)])
        self.assertEqual(expected, md._freeze())

        md = ModifierDimension(FHIR['Account.balance'], "\\FHIR\\")
        expected = OrderedDict([('modifier_path', '\\FHIR\\Account\\balance\\'),
                                ('modifier_cd', 'FHIR:Account.balance'),
                                ('name_char', 'FHIR Account balance'),
                                ('modifier_blob', ''),
                                ('update_date', datetime(2001, 12, 1, 0, 0)),
                                ('download_date', datetime(2017, 5, 25, 0, 0)),
                                ('import_date', datetime(2017, 5, 25, 0, 0)),
                                ('sourcesystem_cd', 'FHIR'),
                                ('upload_id', None)])
        self.assertEqual(expected, md._freeze())

    def test_deep_nesting_1(self):

        ModifierDimension._clear()
        ModifierDimension.sourcesystem_cd = "FHIR STU3"
        ModifierDimension.update_date = datetime(2017, 5, 25, 13, 0)

        ot = FHIRModifierDimension(self.g)
        self.assertEqual([
            ('\\FHIR\\CodeableConcept\\coding\\',
             'FHIR:CodeableConcept.coding',
             'FHIR CodeableConcept coding'),
            ('\\FHIR\\CodeableConcept\\coding\\code\\',
             'FHIR:CodeableConcept.coding.code',
             'FHIR CodeableConcept coding code'),
            ('\\FHIR\\CodeableConcept\\coding\\display\\',
             'FHIR:CodeableConcept.coding.display',
             'FHIR CodeableConcept coding display'),
            ('\\FHIR\\CodeableConcept\\coding\\system\\',
             'FHIR:CodeableConcept.coding.system',
             'FHIR CodeableConcept coding system'),
            ('\\FHIR\\CodeableConcept\\coding\\userSelected\\',
             'FHIR:CodeableConcept.coding.userSelected',
             'FHIR CodeableConcept coding userSelected'),
            ('\\FHIR\\CodeableConcept\\coding\\version\\',
             'FHIR:CodeableConcept.coding.version',
             'FHIR CodeableConcept coding version'),
            ('\\FHIR\\CodeableConcept\\text\\',
             'FHIR:CodeableConcept.text',
             'FHIR CodeableConcept text')],
            list((e.modifier_path, e.modifier_cd, e.name_char) for e in
                 sorted(ot.dimension_list(domain=FHIR.CodeableConcept))))

    def test_deep_nesting_2(self):
        ModifierDimension._clear()
        ModifierDimension.sourcesystem_cd = "FHIR STU3"
        ModifierDimension.update_date = datetime(2017, 5, 25, 13, 0)

        ot = FHIRModifierDimension(self.g)

        self.assertEqual([
                 '\\FHIR\\Observation\\component\\code\\',
                 '\\FHIR\\Observation\\component\\code\\coding\\',
                 '\\FHIR\\Observation\\component\\code\\coding\\code\\',
                 '\\FHIR\\Observation\\component\\code\\coding\\display\\',
                 '\\FHIR\\Observation\\component\\code\\coding\\system\\',
                 '\\FHIR\\Observation\\component\\code\\coding\\userSelected\\',
                 '\\FHIR\\Observation\\component\\code\\coding\\version\\',
                 '\\FHIR\\Observation\\component\\code\\text\\',
                 '\\FHIR\\Observation\\component\\dataAbsentReason\\',
                 '\\FHIR\\Observation\\component\\dataAbsentReason\\coding\\',
                 '\\FHIR\\Observation\\component\\dataAbsentReason\\coding\\code\\',
                 '\\FHIR\\Observation\\component\\dataAbsentReason\\coding\\display\\',
                 '\\FHIR\\Observation\\component\\dataAbsentReason\\coding\\system\\',
                 '\\FHIR\\Observation\\component\\dataAbsentReason\\coding\\userSelected\\',
                 '\\FHIR\\Observation\\component\\dataAbsentReason\\coding\\version\\',
                 '\\FHIR\\Observation\\component\\dataAbsentReason\\text\\',
                 '\\FHIR\\Observation\\component\\interpretation\\',
                 '\\FHIR\\Observation\\component\\interpretation\\coding\\',
                 '\\FHIR\\Observation\\component\\interpretation\\coding\\code\\',
                 '\\FHIR\\Observation\\component\\interpretation\\coding\\display\\',
                 '\\FHIR\\Observation\\component\\interpretation\\coding\\system\\',
                 '\\FHIR\\Observation\\component\\interpretation\\coding\\userSelected\\',
                 '\\FHIR\\Observation\\component\\interpretation\\coding\\version\\',
                 '\\FHIR\\Observation\\component\\interpretation\\text\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\age\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\age\\high\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\age\\low\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\appliesTo\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\appliesTo\\coding\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\appliesTo\\coding\\code\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\appliesTo\\coding\\display\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\appliesTo\\coding\\system\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\appliesTo\\coding\\userSelected\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\appliesTo\\coding\\version\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\appliesTo\\text\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\high\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\low\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\text\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\type\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\type\\coding\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\type\\coding\\code\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\type\\coding\\display\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\type\\coding\\system\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\type\\coding\\userSelected\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\type\\coding\\version\\',
                 '\\FHIR\\Observation\\component\\referenceRange\\type\\text\\',
                 '\\FHIR\\Observation\\component\\valueAttachment\\',
                 '\\FHIR\\Observation\\component\\valueAttachment\\contentType\\',
                 '\\FHIR\\Observation\\component\\valueAttachment\\creation\\',
                 '\\FHIR\\Observation\\component\\valueAttachment\\data\\',
                 '\\FHIR\\Observation\\component\\valueAttachment\\hash\\',
                 '\\FHIR\\Observation\\component\\valueAttachment\\language\\',
                 '\\FHIR\\Observation\\component\\valueAttachment\\size\\',
                 '\\FHIR\\Observation\\component\\valueAttachment\\title\\',
                 '\\FHIR\\Observation\\component\\valueAttachment\\url\\',
                 '\\FHIR\\Observation\\component\\valueCodeableConcept\\',
                 '\\FHIR\\Observation\\component\\valueCodeableConcept\\coding\\',
                 '\\FHIR\\Observation\\component\\valueCodeableConcept\\coding\\code\\',
                 '\\FHIR\\Observation\\component\\valueCodeableConcept\\coding\\display\\',
                 '\\FHIR\\Observation\\component\\valueCodeableConcept\\coding\\system\\',
                 '\\FHIR\\Observation\\component\\valueCodeableConcept\\coding\\userSelected\\',
                 '\\FHIR\\Observation\\component\\valueCodeableConcept\\coding\\version\\',
                 '\\FHIR\\Observation\\component\\valueCodeableConcept\\text\\',
                 '\\FHIR\\Observation\\component\\valueDateTime\\',
                 '\\FHIR\\Observation\\component\\valuePeriod\\',
                 '\\FHIR\\Observation\\component\\valuePeriod\\end\\',
                 '\\FHIR\\Observation\\component\\valuePeriod\\start\\',
                 '\\FHIR\\Observation\\component\\valueQuantity\\',
                 '\\FHIR\\Observation\\component\\valueQuantity\\code\\',
                 '\\FHIR\\Observation\\component\\valueQuantity\\comparator\\',
                 '\\FHIR\\Observation\\component\\valueQuantity\\system\\',
                 '\\FHIR\\Observation\\component\\valueQuantity\\unit\\',
                 '\\FHIR\\Observation\\component\\valueQuantity\\value\\',
                 '\\FHIR\\Observation\\component\\valueRange\\',
                 '\\FHIR\\Observation\\component\\valueRange\\high\\',
                 '\\FHIR\\Observation\\component\\valueRange\\low\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\denominator\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\denominator\\code\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\denominator\\comparator\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\denominator\\system\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\denominator\\unit\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\denominator\\value\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\numerator\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\numerator\\code\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\numerator\\comparator\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\numerator\\system\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\numerator\\unit\\',
                 '\\FHIR\\Observation\\component\\valueRatio\\numerator\\value\\',
                 '\\FHIR\\Observation\\component\\valueSampledData\\',
                 '\\FHIR\\Observation\\component\\valueSampledData\\data\\',
                 '\\FHIR\\Observation\\component\\valueSampledData\\dimensions\\',
                 '\\FHIR\\Observation\\component\\valueSampledData\\factor\\',
                 '\\FHIR\\Observation\\component\\valueSampledData\\lowerLimit\\',
                 '\\FHIR\\Observation\\component\\valueSampledData\\origin\\',
                 '\\FHIR\\Observation\\component\\valueSampledData\\period\\',
                 '\\FHIR\\Observation\\component\\valueSampledData\\upperLimit\\',
                 '\\FHIR\\Observation\\component\\valueString\\',
                 '\\FHIR\\Observation\\component\\valueTime\\'],
                         list(e.modifier_path for e in
                              sorted(ot.dimension_list(domain=FHIR.ObservationComponentComponent))))

if __name__ == '__main__':
    unittest.main()
