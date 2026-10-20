import math
import unittest
from worldloom import numerics as n


class NumericsTests(unittest.TestCase):
    def test_native_box_qp_certifies_kkt_and_replay(self):
        p = {'hessian_diagonal': [2, 4], 'linear': [-6, 8], 'lower': [0, -1], 'upper': [2, 3], 'seed': 7}
        a = n.solve_box_qp(p)
        self.assertEqual(a['status'], 'optimal-certified')
        self.assertEqual(a['primal'], [2, -1])
        self.assertLess(a['residuals']['kkt_inf'], 1e-12)
        fixed = n.solve_box_qp({'hessian_diagonal': [2], 'linear': [-6], 'lower': [1], 'upper': [1]})
        self.assertEqual(fixed['residuals']['kkt_inf'], 0)
        self.assertEqual(a['witness_hash'], n.solve_box_qp(p)['witness_hash'])

    def test_invalid_and_unbounded_problems_do_not_advance(self):
        self.assertEqual(n.solve_box_qp({'hessian_diagonal': [1], 'linear': [0], 'lower': [2], 'upper': [1]})['status'], 'infeasible')
        self.assertEqual(n.solve_box_qp({'hessian_diagonal': [-1], 'linear': [0], 'lower': [0], 'upper': [1]})['status'], 'unsupported')
        self.assertEqual(n.solve_box_qp({'hessian_diagonal': [0], 'linear': [-1], 'lower': [0], 'upper': [None]})['status'], 'unbounded')
        with self.assertRaises(ValueError):
            n.solve_box_qp({'hessian_diagonal': [math.nan], 'linear': [0], 'lower': [0], 'upper': [1]})

    def test_ode_reference_and_budget(self):
        a = n.solve_decay_ode({'rate': .7, 'initial': 3, 'duration': 4, 'steps': 400})
        self.assertLess(abs(a['primal'][0] - 3 * math.exp(-2.8)), 1e-9)
        self.assertEqual(n.solve_decay_ode({'steps': 100001})['status'], 'timed-out')

    def test_game_reports_multiple_and_missing_pure_equilibria(self):
        self.assertEqual(n.solve_game({'row': [[2, 0], [0, 2]], 'column': [[2, 0], [0, 2]]})['status'], 'ambiguous-equilibria')
        self.assertEqual(n.solve_game({'row': [[1, -1], [-1, 1]], 'column': [[-1, 1], [1, -1]]})['status'], 'not-converged')
        cases = n.negotiation_cases()
        self.assertEqual([c['outcome'] for c in cases], ['agreement', 'refusal', 'indeterminate-conflict'])
        self.assertTrue(all(c['tie_break'] and c['objective'] and 'feasible_actions' in c for c in cases))

    def test_camera_jerk_and_resampling(self):
        traces = [n.camera_trace({'fps': fps, 'duration': 6}) for fps in (24, 30, 60, 90)]
        for t in traces:
            self.assertLessEqual(t['metrics']['jerk_max_m_s3'], 25.000001)
            self.assertEqual(t['metrics']['collision_violations'], 0)
            self.assertLess(t['metrics']['jerk_p99_m_s3'], t['baseline']['jerk_p99_m_s3'])
        for t in traces[1:]:
            self.assertLess(abs(t['samples'][-1]['x'] - traces[0]['samples'][-1]['x']), .002)
        with self.assertRaises(ValueError):
            n.camera_trace({'fps': 0})

    def test_weather_divergence_support_and_material_curve(self):
        a = n.weather_field({'time': 2, 'rain': .4, 'initial_wetness': .1})
        self.assertLess(a['metrics']['divergence_inf_s_1'], .002)
        self.assertLessEqual(a['metrics']['speed_max_m_s'], 8)
        self.assertTrue(all(0 <= q['wetness'] <= 1 and .18 <= q['roughness'] <= .82 for q in a['samples']))
        self.assertGreater(a['material']['wet']['reflectance'], a['material']['dry']['reflectance'])
        with self.assertRaises(ValueError):
            n.weather_field({'rain': -1})


if __name__ == '__main__':
    unittest.main()
