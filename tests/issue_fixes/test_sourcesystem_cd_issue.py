
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
