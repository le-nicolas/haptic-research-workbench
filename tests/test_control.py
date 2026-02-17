import unittest

import numpy as np

from interactive_haptics.control import simulate_admittance, simulate_pid


class ControlSimulationTests(unittest.TestCase):
    def test_pid_moves_toward_target(self) -> None:
        target = 0.2
        result = simulate_pid(duration=2.0, target=target)
        final_position = float(result["position"][-1])
        initial_error = abs(target - 0.0)
        final_error = abs(target - final_position)
        self.assertLess(final_error, initial_error)
        self.assertGreater(final_position, 0.05)

    def test_pid_has_stable_shapes(self) -> None:
        result = simulate_pid(duration=1.0, dt=0.02)
        n = len(result["time"])
        self.assertEqual(n, len(result["position"]))
        self.assertEqual(n, len(result["velocity"]))
        self.assertEqual(n, len(result["control"]))
        self.assertTrue(np.all(np.isfinite(result["control"])))

    def test_admittance_zero_force_stays_near_origin(self) -> None:
        result = simulate_admittance(
            force_amplitude=0.0,
            stiffness=50.0,
            damping=12.0,
            duration=2.0,
        )
        self.assertAlmostEqual(float(result["position"][-1]), 0.0, places=6)
        self.assertAlmostEqual(float(result["velocity"][-1]), 0.0, places=6)


if __name__ == "__main__":
    unittest.main()
