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

import unittest

from rdflib import Graph

from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact
from i2b2model.data.i2b2observationfact import ObservationFact, ObservationFactKey
from dynprops import clear


class SourcesystemCdTestCase(unittest.TestCase):
    def test_sourcesystem_cd(self):
        clear(ObservationFact)
        ofk = ObservationFactKey(1, 1, "Provider")
        obsf = ObservationFact(ofk, "FHIR:Test")
        fobsf = FHIRObservationFact(Graph(), ofk, "FHIR:test", None, None)
        if obsf.sourcesystem_cd != "Unspecified":
            print("HERE")
        self.assertEqual("Unspecified", obsf.sourcesystem_cd)
        self.assertEqual("Unspecified", fobsf.sourcesystem_cd)

        cd1 = "SourceSystemCdTestCase_cd1"
        cd2 = "SourceSystemCdTestCase_cd2"
        ObservationFact.sourcesystem_cd = cd1
        FHIRObservationFact.sourcesystem_cd = cd2

        self.assertEqual(cd2, obsf.sourcesystem_cd)
        self.assertEqual(cd2, fobsf.sourcesystem_cd)
        clear(ObservationFact)
        self.assertEqual("Unspecified", obsf.sourcesystem_cd)
        self.assertEqual("Unspecified", fobsf.sourcesystem_cd)

        ObservationFact.sourcesystem_cd = cd1
        FHIRObservationFact.sourcesystem_cd = cd2
        self.assertEqual(cd2, obsf.sourcesystem_cd)
        self.assertEqual(cd2, fobsf.sourcesystem_cd)
        clear(FHIRObservationFact)
        self.assertEqual("Unspecified", obsf.sourcesystem_cd)
        self.assertEqual("Unspecified", fobsf.sourcesystem_cd)

        ObservationFact.sourcesystem_cd = cd1
        self.assertEqual(cd1, obsf.sourcesystem_cd)
        self.assertEqual(cd1, fobsf.sourcesystem_cd)
        clear(FHIRObservationFact)
        self.assertEqual("Unspecified", obsf.sourcesystem_cd)
        self.assertEqual("Unspecified", fobsf.sourcesystem_cd)


if __name__ == '__main__':
    unittest.main()
