import unittest

import numpy as np

from interactive_haptics.control import (
    simulate_admittance,
    simulate_pid,
    simulate_virtual_wall,
    virtual_wall_force,
)


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

    def test_virtual_wall_no_contact_has_no_force(self) -> None:
        force = virtual_wall_force(
            position=0.45,
            velocity=0.2,
            wall_position=0.7,
            stiffness=300.0,
            damping=4.0,
            friction=0.3,
            max_force=50.0,
        )
        self.assertEqual(force, 0.0)

    def test_virtual_wall_contact_pushes_back(self) -> None:
        force = virtual_wall_force(
            position=0.82,
            velocity=0.1,
            wall_position=0.7,
            stiffness=200.0,
            damping=2.0,
            friction=0.1,
            max_force=100.0,
        )
        self.assertLess(force, 0.0)

    def test_virtual_wall_force_clipping(self) -> None:
        force = virtual_wall_force(
            position=0.95,
            velocity=2.0,
            wall_position=0.6,
            stiffness=1000.0,
            damping=10.0,
            friction=0.2,
            max_force=20.0,
        )
        self.assertAlmostEqual(force, -20.0, places=6)

    def test_virtual_wall_simulation_shapes(self) -> None:
        result = simulate_virtual_wall(duration=2.0, dt=0.02)
        n = len(result["time"])
        self.assertEqual(n, len(result["position"]))
        self.assertEqual(n, len(result["velocity"]))
        self.assertEqual(n, len(result["force"]))
        self.assertEqual(n, len(result["penetration"]))
        self.assertTrue(np.all(result["penetration"] >= 0.0))


if __name__ == "__main__":
    unittest.main()
