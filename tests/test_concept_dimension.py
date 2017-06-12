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
from collections import OrderedDict
from datetime import datetime

from rdflib import Namespace

from i2fhirb2.fhir.fhirspecific import W5, FHIR
from i2fhirb2.i2b2model.i2b2conceptdimension import ConceptDimensionRoot
from tests.base_test_case import BaseTestCase, shared_graph


class ConceptDimensionTestCase(BaseTestCase):

    w5ns = Namespace("http://hl7.org/fhir/w5#")
    fhirns = Namespace("http://hl7.org/fhir/")

    def test_basics(self):
        from i2fhirb2.i2b2model.i2b2conceptdimension import ConceptDimension

        ConceptDimension.graph = shared_graph
        ConceptDimension.download_date = datetime(2017, 5, 25)
        ConceptDimension.sourcesystem_cd = "FHIR"
        ConceptDimension.import_date = datetime(2017, 5, 25)

        cd = ConceptDimension(W5.administrative, "\\FHIR\\w5\\")
        self.assertAlmostNow(cd.update_date)
        ConceptDimension.update_date = datetime(2001, 12, 1)
        expected = OrderedDict([('concept_path', '\\FHIR\\w5\\administrative\\'),
                                ('concept_cd', 'W5:administrative'),
                                ('name_char', 'W5 administrative'),
                                ('concept_blob', ''),
                                ('update_date', datetime(2001, 12, 1, 0, 0)),
                                ('download_date', datetime(2017, 5, 25, 0, 0)),
                                ('import_date', datetime(2017, 5, 25, 0, 0)),
                                ('sourcesystem_cd', 'FHIR'),
                                ('upload_id', None)])
        self.assertEqual(expected, cd._freeze())

        # Note - balance is actually a modifier.  This is strictly an example
        cd = ConceptDimension(FHIR['Account.balance'], "\\FHIR\\financial\\support\\")
        expected = OrderedDict([('concept_path', '\\FHIR\\financial\\support\\Account\\balance\\'),
                                ('concept_cd', 'FHIR:Account.balance'),
                                ('name_char', 'FHIR Account balance'),
                                ('concept_blob', ''),
                                ('update_date', datetime(2001, 12, 1, 0, 0)),
                                ('download_date', datetime(2017, 5, 25, 0, 0)),
                                ('import_date', datetime(2017, 5, 25, 0, 0)),
                                ('sourcesystem_cd', 'FHIR'),
                                ('upload_id', None)])
        self.assertEqual(expected, cd._freeze())

    def test_interactions(self):
        """
        ModifierDimension and ConceptDimension share a common root.  If the dynelements lists are not specific to the
        subclasses, we end up with one composite
        """
        from i2fhirb2.i2b2model.i2b2conceptdimension import ConceptDimension
        from i2fhirb2.i2b2model.i2b2modifierdimension import ModifierDimension

        self.assertEqual('modifier_path\tmodifier_cd\tname_char\tmodifier_blob\tupdate_date\t'
                         'download_date\timport_date\tsourcesystem_cd\tupload_id', ModifierDimension._header())
        self.assertEqual('concept_path\tconcept_cd\tname_char\tconcept_blob\tupdate_date\t'
                         'download_date\timport_date\tsourcesystem_cd\tupload_id', ConceptDimension._header())

    def test_fhir_conceptdimensionroot(self):
        cdr = ConceptDimensionRoot('FHIR')
        ConceptDimensionRoot.update_date = datetime(2017, 5, 25)
        self.assertEqual(OrderedDict([
             ('concept_path', '\\FHIR\\'),
             ('concept_cd', 'FHIR'),
             ('name_char', 'FHIR root'),
             ('concept_blob', ''),
             ('update_date', datetime(2017, 5, 25, 0, 0)),
             ('download_date', datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'Unspecified'),
             ('upload_id', None)]), cdr._freeze())

if __name__ == '__main__':
    unittest.main()
