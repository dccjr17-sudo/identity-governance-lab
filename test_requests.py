import unittest

from access_requests import create_request


class RequestTests(unittest.TestCase):
    def setUp(self):
        self.identities = {
            "E103": {"status": "active", "manager_id": "E900", "department": "Finance", "baseline_access": ["email.user"]},
            "E900": {"status": "active"},
            "E999": {"status": "active"},
        }
        self.catalog = {"entitlements": {
            "erp.payment.create": {"requestable": True, "owner": "E900"},
            "email.user": {"requestable": False, "owner": "E900"},
        }}

    def test_request_remains_pending_with_two_stages(self):
        request = create_request("E103", "erp.payment.create", "Pay approved invoices", self.identities, self.catalog)
        self.assertFalse(request["access_granted"])
        self.assertEqual(request["status"], "pending")
        self.assertEqual([s["stage"] for s in request["approval_stages"]], ["manager", "application_owner"])

    def test_terminated_worker_rejected(self):
        self.identities["E103"]["status"] = "terminated"
        with self.assertRaises(ValueError):
            create_request("E103", "erp.payment.create", "Reason", self.identities, self.catalog)

    def test_self_review_routes_to_sponsor(self):
        self.identities["E103"]["manager_id"] = "E103"
        request = create_request("E103", "erp.payment.create", "Reason", self.identities, self.catalog)
        self.assertEqual(request["approval_stages"][0]["reviewer_id"], "E999")

    def test_blank_reason_and_nonrequestable_access_rejected(self):
        for entitlement, reason in [("erp.payment.create", " "), ("email.user", "Reason")]:
            with self.assertRaises(ValueError):
                create_request("E103", entitlement, reason, self.identities, self.catalog)


if __name__ == "__main__":
    unittest.main()
