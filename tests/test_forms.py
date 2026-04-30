import unittest
from unittest.mock import MagicMock, patch
from modules.forms import edit_forms_logic
from core.utils import load_i18n
from modules.forms_scripts import build_edit_forms_script

class TestForms(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_edit_forms_batch(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["extrude:OK:Form1"]}
        mock_post.return_value = mock_response

        ops = [{"action": "extrude", "sketch": "Sketch1", "dist": 5.0}]
        res = edit_forms_logic(ops, "en")
        self.assertEqual(res, "Forms (T-Splines) updated successfully.")

    def test_edit_forms_script_assigns_semantic_names(self):
        script = build_edit_forms_script()
        self.assertIn("pick_form_name", script)
        self.assertIn("ensure_unique_body_name", script)
        self.assertIn("FormExtrude", script)

if __name__ == '__main__':
    unittest.main()
