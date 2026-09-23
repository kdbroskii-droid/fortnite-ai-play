import unittest
from src.action_model import Action
from src.macro_validator import validate_actions

class MacroValidatorTests(unittest.TestCase):
    def test_valid_actions(self):
        validate_actions([
            Action("key_down", "W"),
            Action("delay", 50),
            Action("key_up", "W"),
        ])

    def test_invalid_mouse_move(self):
        with self.assertRaises(ValueError):
            validate_actions([Action("mouse_move")])

if __name__ == "__main__":
    unittest.main()
