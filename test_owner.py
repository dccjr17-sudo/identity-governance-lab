from copy import deepcopy
import unittest

import test_reviews
from review_owner import review_owner


class OwnerReviewTests(unittest.TestCase):
    def setUp(self):
        fixture = test_reviews.ManagerReviewTests()
        fixture.setUp()
        self.identities, self.catalog, self.request = fixture.identities, fixture.catalog, fixture.request
        self.catalog["sod_rules"] = [{"id": "SOD-001", "description": "Conflicting payment permissions",
                                      "incompatible_entitlements": ["erp.payment.create", "erp.payment.approve"]}]
        fixture.review()

    def review(self, reviewer="E900", other_requests=None):
        return review_owner(self.request, reviewer, "approve", "Owner reviewed", self.identities,
                            self.catalog, other_requests or [self.request])

    def test_two_approvals_grant_simulated_access(self):
        self.assertTrue(self.review()["access_granted"])

    def test_missing_manager_approval_rejected(self):
        self.request["approval_stages"][0]["decision"] = "pending"
        with self.assertRaises(ValueError):
            self.review()

    def test_wrong_owner_rejected_without_mutation(self):
        before = deepcopy(self.request)
        with self.assertRaises(ValueError):
            self.review("E901")
        self.assertEqual(self.request, before)

    def test_conflict_blocks_grant_without_mutation(self):
        before = deepcopy(self.request)
        with self.assertRaises(ValueError):
            self.review(other_requests=[{"employee_id": "E103", "entitlement": "erp.payment.approve", "access_granted": True}])
        self.assertEqual(self.request, before)

    def test_terminated_requester_rejected(self):
        self.identities["E103"]["status"] = "terminated"
        with self.assertRaises(ValueError):
            self.review()


if __name__ == "__main__":
    unittest.main()
