from decimal import Decimal as D
import unittest


def decision_value(prob_bad, bad_execution, bad_rejection, query_cost, allowed):
    costs = {"execute": prob_bad * bad_execution,
             "reject": (1 - prob_bad) * bad_rejection}
    baseline = min(costs[d] for d in allowed)
    # Fixture only: a perfect, timely, authorized query permits the correct
    # zero-loss terminal action in both states. No business data is used.
    return baseline, baseline - query_cost


class DecisionCostCases(unittest.TestCase):
    def test_case_a(self):
        self.assertEqual(decision_value(D('.02'), 1000, 30, 4, ('execute', 'reject')),
                         (D('20'), D('16')))

    def test_case_b(self):
        self.assertEqual(decision_value(D('.02'), 1000, 30, 4, ('reject',)),
                         (D('29.4'), D('25.4')))

    def test_case_c(self):
        # Authorized human review resolves both states at all-in cost 3.
        base, _ = decision_value(D('.02'), 1000, 30, 4, ('reject',))
        self.assertEqual(min(base, D('3')) - D('4'), D('-1'))


if __name__ == '__main__':
    unittest.main()
