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

from i2b2model.shared.i2b2core import I2B2Core
from rdflib import Graph

from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact
from i2b2model.data.i2b2observationfact import ObservationFact, ObservationFactKey
from dynprops import clear

from i2fhirb2.fhir.fhirspecific import DEFAULT_SOURCE_SYSTEM


class SourcesystemCdTestCase(unittest.TestCase):
    def test_sourcesystem_cd(self):
        clear(ObservationFact)
        ofk = ObservationFactKey(1, 1, "Provider")
        obsf = ObservationFact(ofk, "FHIR:Test")
        fobsf = FHIRObservationFact(Graph(), ofk, "FHIR:test", None, None)

        self.assertEqual(DEFAULT_SOURCE_SYSTEM, obsf.sourcesystem_cd)
        self.assertEqual(DEFAULT_SOURCE_SYSTEM, fobsf.sourcesystem_cd)

        cd1 = "SourceSystemCdTestCase_cd1"
        cd2 = "SourceSystemCdTestCase_cd2"
        I2B2Core.sourcesystem_cd = cd1

        self.assertEqual(cd1, obsf.sourcesystem_cd)
        self.assertEqual(cd1, fobsf.sourcesystem_cd)
        clear(I2B2Core)
        I2B2Core.sourcesystem_cd = DEFAULT_SOURCE_SYSTEM
        self.assertEqual(DEFAULT_SOURCE_SYSTEM, obsf.sourcesystem_cd)
        self.assertEqual(DEFAULT_SOURCE_SYSTEM, fobsf.sourcesystem_cd)

        I2B2Core.sourcesystem_cd = cd1
        self.assertEqual(cd1, obsf.sourcesystem_cd)
        self.assertEqual(cd1, fobsf.sourcesystem_cd)
        clear(I2B2Core)
        I2B2Core.sourcesystem_cd = DEFAULT_SOURCE_SYSTEM
        self.assertEqual(DEFAULT_SOURCE_SYSTEM, obsf.sourcesystem_cd)
        self.assertEqual(DEFAULT_SOURCE_SYSTEM, fobsf.sourcesystem_cd)

        I2B2Core.sourcesystem_cd = cd1
        self.assertEqual(cd1, obsf.sourcesystem_cd)
        self.assertEqual(cd1, fobsf.sourcesystem_cd)
        clear(I2B2Core)
        I2B2Core.sourcesystem_cd = DEFAULT_SOURCE_SYSTEM
        self.assertEqual(DEFAULT_SOURCE_SYSTEM, obsf.sourcesystem_cd)
        self.assertEqual(DEFAULT_SOURCE_SYSTEM, fobsf.sourcesystem_cd)


if __name__ == '__main__':
    unittest.main()
