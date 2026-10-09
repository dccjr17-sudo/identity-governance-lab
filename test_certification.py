import unittest
from copy import deepcopy

from certify_access import certify


class CertificationTests(unittest.TestCase):
    def setUp(self):
        self.request = {"employee_id": "E103", "entitlement": "erp.payment.create", "status": "approved",
                        "access_granted": True, "department_at_request": "Finance"}
        self.identities = {"E103": {"status": "active", "manager_id": "E900", "department": "Finance"},
                           "E900": {"status": "active"}, "E901": {"status": "active"}}

    def test_revoke_removes_grant_and_records_reason(self):
        event = certify(self.request, "E900", "revoke", "Duties changed", self.identities)
        self.assertFalse(self.request["access_granted"])
        self.assertEqual(self.request["status"], "revoked")
        self.assertTrue(event["removal_completed"])
        self.assertEqual(self.request["certification_history"][0]["reason"], "Duties changed")

    def test_keep_retains_grant(self):
        certify(self.request, "E900", "keep", "Still needed", self.identities)
        self.assertTrue(self.request["access_granted"])

    def test_wrong_reviewer_and_self_review_do_not_mutate(self):
        before = deepcopy(self.request)
        for reviewer in ["E103", "E901"]:
            with self.assertRaises(ValueError):
                certify(self.request, reviewer, "revoke", "Reason", self.identities)
        self.assertEqual(self.request, before)

    def test_revoked_access_cannot_be_kept_or_revoked_again(self):
        certify(self.request, "E900", "revoke", "Reason", self.identities)
        with self.assertRaises(ValueError):
            certify(self.request, "E900", "keep", "Reason", self.identities)

    def test_terminated_identity_cannot_retain_grant(self):
        self.identities["E103"]["status"] = "terminated"
        with self.assertRaises(ValueError):
            certify(self.request, "E900", "keep", "Reason", self.identities)


if __name__ == "__main__":
    unittest.main()
