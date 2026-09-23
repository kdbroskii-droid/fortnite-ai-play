import unittest
from src.aim_simulator import AimConfig, simulate_magazine

class AimSimulatorTests(unittest.TestCase):
    def test_probabilities_total_100(self):
        AimConfig().validate()

    def test_deterministic_seed(self):
        a = simulate_magazine(30, seed=123)
        b = simulate_magazine(30, seed=123)
        self.assertEqual(a, b)

    def test_magazine_size(self):
        self.assertEqual(len(simulate_magazine(30, seed=1)), 30)

if __name__ == "__main__":
    unittest.main()
