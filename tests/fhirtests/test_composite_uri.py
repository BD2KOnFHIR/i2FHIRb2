
import unittest

test_list = [("Account.guarantor.period", "Period.end", "Account.guarantor.period.end"),
             ("ActivityDefinition.participant.role.coding", "Coding.code",
              "ActivityDefinition.participant.role.coding.code"),
             ("AuditEvent.agent.network", "AuditEvent.agent.network.address", "AuditEvent.agent.network.address"),
             ("Bundle.entry.request", "Bundle.entry.request.ifMatch", "Bundle.entry.request.ifMatch"),
             ("ClaimResponse.addItem.adjudication", "ClaimResponse.item.adjudication.amount",
              "ClaimResponse.addItem.adjudication.amount"),
             ("Bundle.entry.link", "Bundle.link.relation", "Bundle.entry.link.relation")]


class CompositeURITestCase(unittest.TestCase):
    """ Test composite URI construction

    """
    def test1(self):
        from i2fhirb2.fhir.fhirspecific import composite_uri, FHIR
        for parent, mod, rslt in test_list:
            self.assertEqual(FHIR[rslt], composite_uri(FHIR[parent], FHIR[mod]))


if __name__ == '__main__':
    unittest.main()
