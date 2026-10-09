import unittest
from reconcile_hr import reconcile_requests


class RequestLifecycleTests(unittest.TestCase):
    def request(self, status="approved", grant=True):
        return {"request_id": "REQ-test", "employee_id": "E104", "entitlement": "erp.invoice.read",
                "status": status, "access_granted": grant, "department_at_request": "Sales",
                "approval_stages": [{"stage": "manager", "reviewer_id": "E902"}]}

    def test_termination_revokes_and_cancels(self):
        identities = {"E104": {"department": "Sales", "manager_id": "E902", "status": "terminated"}}
        original = [self.request(), self.request("pending", False)]
        updated, changes = reconcile_requests(original, identities)
        self.assertEqual([r["status"] for r in updated], ["revoked", "cancelled"])
        self.assertTrue(all(not r["access_granted"] for r in updated))
        self.assertEqual(len(changes), 2)
        self.assertTrue(original[0]["access_granted"])
        repeated, changes = reconcile_requests(updated, identities)
        self.assertEqual(repeated, updated)
        self.assertEqual(changes, [])

    def test_transfer_revokes_additional_access(self):
        updated, _ = reconcile_requests([self.request()], {"E104": {"department": "IT", "manager_id": "E901", "status": "active"}})
        self.assertEqual(updated[0]["status"], "revoked")

    def test_manager_change_cancels_pending_request(self):
        updated, _ = reconcile_requests([self.request("pending", False)], {"E104": {"department": "Sales", "manager_id": "E999", "status": "active"}})
        self.assertEqual(updated[0]["status"], "cancelled")

    def test_missing_identity_and_old_denial_are_preserved(self):
        for requests, identities in [([self.request()], {}),
                ([self.request("denied", False)], {"E104": {"department": "Sales", "manager_id": "E902", "status": "terminated"}})]:
            updated, changes = reconcile_requests(requests, identities)
            self.assertEqual(updated, requests)
            self.assertEqual(changes, [])


if __name__ == "__main__":
    unittest.main()
