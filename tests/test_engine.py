import unittest
from engine import Policy, decide, new_proposal, resolve

class PolicyEngineTests(unittest.TestCase):
    def setUp(self):
        self.policy = Policy(100, ("Office Supplies",))

    def test_valid_purchase_requires_approval(self):
        self.assertEqual(decide(49.99, "Office Supplies", self.policy)[0], "PENDING_APPROVAL")

    def test_exact_limit_allowed(self):
        self.assertEqual(decide(100, "Office Supplies", self.policy)[0], "PENDING_APPROVAL")

    def test_over_limit_blocked(self):
        self.assertEqual(decide(150, "Office Supplies", self.policy)[0], "BLOCKED")

    def test_unknown_merchant_blocked(self):
        self.assertEqual(decide(30, "Unknown Merchant", self.policy)[0], "BLOCKED")

    def test_nonpositive_amount_blocked(self):
        for amount in (0, -1):
            self.assertEqual(decide(amount, "Office Supplies", self.policy)[0], "BLOCKED")

    def test_approval_is_simulated(self):
        tx = new_proposal("Office Supplies", 49.99, "Demo", self.policy)
        resolve(tx, True)
        self.assertEqual(tx["status"], "SIMULATED_APPROVED")
        self.assertIn("PAYMENT_NOT_EXECUTED", [e["type"] for e in tx["events"]])

    def test_rejection(self):
        tx = new_proposal("Office Supplies", 49.99, "Demo", self.policy)
        resolve(tx, False)
        self.assertEqual(tx["status"], "REJECTED")

    def test_blocked_cannot_be_approved(self):
        tx = new_proposal("Office Supplies", 150, "Demo", self.policy)
        with self.assertRaises(ValueError):
            resolve(tx, True)

if __name__ == "__main__":
    unittest.main()
