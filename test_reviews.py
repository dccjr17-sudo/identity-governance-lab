import unittest

from access_requests import create_request
from review_request import review_manager


class ManagerReviewTests(unittest.TestCase):
    def setUp(self):
        self.identities = {
            "E103": {"status": "active", "manager_id": "E900", "department": "Finance", "baseline_access": []},
            "E900": {"status": "active"}, "E901": {"status": "active"},
        }
        self.catalog = {"entitlements": {"erp.payment.create": {"requestable": True, "owner": "E900"}}}
        self.request = create_request("E103", "erp.payment.create", "Business need", self.identities, self.catalog)

    def review(self, reviewer="E900", decision="approve"):
        return review_manager(self.request, reviewer, decision, "Reviewed need", self.identities, self.catalog)

    def test_manager_approval_does_not_grant_access(self):
        result = self.review()
        self.assertEqual(result["status"], "pending")
        self.assertFalse(result["access_granted"])
        self.assertEqual(result["approval_stages"][1]["decision"], "pending")

    def test_wrong_reviewer_and_self_approval_rejected(self):
        for reviewer in ["E901", "E103"]:
            with self.assertRaises(ValueError):
                self.review(reviewer)
        self.assertEqual(self.request["approval_stages"][0]["decision"], "pending")

    def test_termination_or_transfer_prevents_review(self):
        self.identities["E103"]["status"] = "terminated"
        with self.assertRaises(ValueError):
            self.review()
        self.identities["E103"]["status"] = "active"
        self.identities["E103"]["department"] = "IT"
        with self.assertRaises(ValueError):
            self.review()

    def test_denial_is_terminal(self):
        self.assertEqual(self.review(decision="deny")["status"], "denied")
        with self.assertRaises(ValueError):
            self.review()

    def test_duplicate_review_rejected(self):
        self.review()
        with self.assertRaises(ValueError):
            self.review()


if __name__ == "__main__":
    unittest.main()
