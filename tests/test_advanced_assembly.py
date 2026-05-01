import unittest
from unittest.mock import MagicMock, patch
from modules.assembly import edit_assembly_logic
from core.utils import load_i18n
from modules.assembly_scripts import build_edit_assembly_script

class TestAdvancedAssembly(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_edit_assembly_as_built_joint(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["create_as_built_joint:OK"]}
        mock_post.return_value = mock_response

        ops = [{
            "action": "create_as_built_joint",
            "component1_path": "Root/A",
            "component2_path": "Root/B",
            "type": "Revolute"
        }]
        res = edit_assembly_logic(ops, "en")
        self.assertEqual(res, "Assembly updated successfully.")

    @patch('core.bridge.requests.post')
    def test_edit_assembly_set_contact_sets(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["set_contact_sets:OK:True"]}
        mock_post.return_value = mock_response

        ops = [{"action": "set_contact_sets", "enable": True}]
        res = edit_assembly_logic(ops, "en")
        self.assertEqual(res, "Assembly updated successfully.")

    def test_edit_assembly_script_has_mechanical_features(self):
        script = build_edit_assembly_script()
        self.assertIn("elif action == 'create_as_built_joint':", script)
        self.assertIn("joints = root.asBuiltJoints", script)
        self.assertIn("elif action == 'set_contact_sets':", script)
        self.assertIn("design.isContactAnalysisEnabled = enable", script)

if __name__ == '__main__':
    unittest.main()
