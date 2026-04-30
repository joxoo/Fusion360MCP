import unittest
from unittest.mock import MagicMock, patch
from modules.surfaces import edit_surfaces_logic
from core.utils import load_i18n
from modules.surfaces_scripts import build_edit_surfaces_script

class TestSurfaces(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_edit_surfaces_batch(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["patch:OK:Body1"]}
        mock_post.return_value = mock_response

        ops = [{"action": "patch", "sketch": "Sketch1"}]
        res = edit_surfaces_logic(ops, "en")
        self.assertEqual(res, "Surfaces updated successfully.")

    def test_edit_surfaces_script_assigns_semantic_names(self):
        script = build_edit_surfaces_script()
        self.assertIn("pick_surface_name", script)
        self.assertIn("ensure_unique_body_name", script)
        self.assertIn("Patch", script)
        self.assertIn("Offset", script)
        self.assertIn("Thicken", script)

if __name__ == '__main__':
    unittest.main()
