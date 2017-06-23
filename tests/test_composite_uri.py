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

from i2fhirb2.fhir.fhirspecific import FHIR

test_list = [("Account.guarantor.period", "Period.end", "Account.guarantor.period.end"),
             ("ActivityDefinition.participant.role.coding", "Coding.code",
              "ActivityDefinition.participant.role.coding.code"),
             ("AuditEvent.agent.network", "AuditEvent.agent.network.address", "AuditEvent.agent.network.address"),
             ("Bundle.entry.request", "Bundle.entry.request.ifMatch", "Bundle.entry.request.ifMatch"),
             ("ClaimResponse.addItem.adjudication", "ClaimResponse.item.adjudication.amount",
              "ClaimResponse.addItem.adjudication.amount"),
             ("Bundle.entry.link", "Bundle.link.relation", "Bundle.entry.link.relation")]


class CompositeURITestCase(unittest.TestCase):
    def test1(self):
        from i2fhirb2.fhir.fhirmetadata import FHIRMetadata
        for parent, mod, rslt in test_list:
            self.assertEqual(FHIR[rslt], FHIRMetadata.composite_uri(FHIR[parent], FHIR[mod]))


if __name__ == '__main__':
    unittest.main()
