import unittest
from reconcile_hr import reconcile


class ReconciliationTests(unittest.TestCase):
    def test_mover_removes_old_access_and_retains_email(self):
        original = {"E100": {"department": "Finance", "status": "active", "baseline_access": ["email.user", "erp.invoice.read"]}}
        state, _ = reconcile({}, original)
        moved = {"E100": {"department": "IT", "status": "active", "baseline_access": ["email.user", "helpdesk.agent"]}}
        updated, changes = reconcile(state, moved)
        self.assertEqual(changes[0]["removed"], ["erp.invoice.read"])
        self.assertEqual(changes[0]["added"], ["helpdesk.agent"])
        self.assertEqual(changes[0]["retained"], ["email.user"])
        self.assertEqual(len(updated["history"]), 2)
        self.assertEqual(state["identities"]["E100"]["department"], "Finance")

    def test_leaver_and_repeat_import(self):
        active = {"E102": {"status": "active", "baseline_access": ["email.user", "crm.user"]}}
        state, _ = reconcile({}, active)
        terminated = {"E102": {"status": "terminated", "baseline_access": []}}
        state, changes = reconcile(state, terminated)
        self.assertEqual(changes[0]["removed"], ["crm.user", "email.user"])
        repeated, changes = reconcile(state, terminated)
        self.assertEqual(changes, [])
        self.assertEqual(repeated, state)

    def test_missing_row_does_not_delete_identity(self):
        state, _ = reconcile({}, {"E100": {"status": "active", "baseline_access": ["email.user"]}})
        updated, changes = reconcile(state, {})
        self.assertEqual(updated, state)
        self.assertEqual(changes, [])


if __name__ == "__main__":
    unittest.main()
