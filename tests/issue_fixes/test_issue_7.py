
import unittest

from tests.utils.load_facts_helper import LoadFactsHelper

# TODO: This issue is NOT fixed!  There is a temporary patch in FHIRObservationFactFactory.skip_predicates that
#       ignores Observation.referenceRange


class ReferenceRangeIssue(LoadFactsHelper):
    caller_filename = __file__

    def test_reference_range(self):
        """ The example below fails with a duplicate key violation """
        with self.sourcesystem_cd():
            self.load_named_resource('obs_sample_1134281.ttl')
            self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
