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

from rdflib import Graph, RDFS

from i2fhirb2.fhir.fhirspecific import concept_path
from tests.utils.base_test_case import test_data_directory


class W5TestCase(unittest.TestCase):

    def test_w5_concepts(self):
        from i2fhirb2.fhir.fhirontologytable import FHIROntologyTable
        g = Graph()
        g.load(os.path.join(test_data_directory, 'fhir_metadata_vocabulary', 'w5.ttl'), format="turtle")
        self.assertEqual([
             'http://hl7.org/fhir/w5#administrative',
             'http://hl7.org/fhir/w5#administrative.device',
             'http://hl7.org/fhir/w5#administrative.entity',
             'http://hl7.org/fhir/w5#administrative.group',
             'http://hl7.org/fhir/w5#administrative.individual',
             'http://hl7.org/fhir/w5#clinical',
             'http://hl7.org/fhir/w5#clinical.careprovision',
             'http://hl7.org/fhir/w5#clinical.diagnostics',
             'http://hl7.org/fhir/w5#clinical.general',
             'http://hl7.org/fhir/w5#clinical.medication',
             'http://hl7.org/fhir/w5#financial',
             'http://hl7.org/fhir/w5#financial.billing',
             'http://hl7.org/fhir/w5#financial.other',
             'http://hl7.org/fhir/w5#financial.payment',
             'http://hl7.org/fhir/w5#financial.support',
             'http://hl7.org/fhir/w5#workflow',
             'http://hl7.org/fhir/w5#workflow.encounter',
             'http://hl7.org/fhir/w5#workflow.order',
             'http://hl7.org/fhir/w5#workflow.scheduling'],
            [str(e) for e in sorted(FHIROntologyTable(g).w5_concepts())])

    def test_w5_paths(self):
        from i2fhirb2.fhir.fhirontologytable import FHIROntologyTable
        g = Graph()
        g.load(os.path.join(test_data_directory, 'fhir_metadata_vocabulary', 'w5.ttl'), format="turtle")
        fot = FHIROntologyTable(g)
        rval = []
        for subj in fot.w5_concepts():
            for path in fot.i2b2_paths('\\FHIR\\', subj, RDFS.subClassOf):
                rval.append(path + concept_path(subj))

        self.assertEqual([
             '\\FHIR\\administrative\\',
             '\\FHIR\\administrative\\device\\',
             '\\FHIR\\administrative\\entity\\',
             '\\FHIR\\administrative\\group\\',
             '\\FHIR\\administrative\\individual\\',
             '\\FHIR\\clinical\\',
             '\\FHIR\\clinical\\careprovision\\',
             '\\FHIR\\clinical\\diagnostics\\',
             '\\FHIR\\clinical\\general\\',
             '\\FHIR\\clinical\\medication\\',
             '\\FHIR\\financial\\',
             '\\FHIR\\financial\\billing\\',
             '\\FHIR\\financial\\other\\',
             '\\FHIR\\financial\\payment\\',
             '\\FHIR\\financial\\support\\',
             '\\FHIR\\workflow\\',
             '\\FHIR\\workflow\\encounter\\',
             '\\FHIR\\workflow\\order\\',
             '\\FHIR\\workflow\\scheduling\\'], sorted(rval))

if __name__ == '__main__':
    unittest.main()