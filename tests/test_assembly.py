import unittest
from unittest.mock import MagicMock, patch
from modules.assembly import edit_assembly_logic
from core.utils import load_i18n
from modules.assembly_scripts import build_edit_assembly_script

class TestAssembly(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_edit_assembly_batch(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["create_component:OK:Comp1"]}
        mock_post.return_value = mock_response

        ops = [{"action": "create_component", "name": "Comp1"}]
        res = edit_assembly_logic(ops, "en")
        self.assertEqual(res, "Assembly updated successfully.")

    @patch('core.bridge.requests.post')
    def test_edit_assembly_joint_component_paths_are_forwarded(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["create_joint:OK"]}
        mock_post.return_value = mock_response

        ops = [{
            "action": "create_joint",
            "component1_path": "Root/Frame/Base",
            "component2_path": "Root/Frame/Arm",
            "type": "Rigid",
        }]
        res = edit_assembly_logic(ops, "en")

        self.assertEqual(res, "Assembly updated successfully.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['operations'][0]['component1_path'], "Root/Frame/Base")
        self.assertEqual(params['operations'][0]['component2_path'], "Root/Frame/Arm")

    def test_edit_assembly_script_uses_unified_component_resolution(self):
        script = build_edit_assembly_script()
        self.assertIn("resolve_component_context(payload.get(name_key), payload.get(path_key))", script)
        self.assertIn("component1_name", script)
        self.assertIn("component1_path", script)
        self.assertIn("component2_name", script)
        self.assertIn("component2_path", script)
        self.assertIn("legacy_key", script)
        self.assertIn("create_joint:ERR_COMPONENT", script.replace("{action}:", "create_joint:"))
        self.assertIn("occ.activate()", script)
        self.assertIn("ERR_VERIFICATION_FAILED", script)
        self.assertIn("rename_component", script)
        self.assertIn("delete_component", script)
        self.assertIn("move_component", script)
        self.assertIn("current_translation", script)
        self.assertIn("target_component_path", script)

    @patch('core.bridge.requests.post')
    def test_edit_assembly_surfaces_batch_errors(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["create_component:ERR_VERIFICATION_FAILED"]}
        mock_post.return_value = mock_response

        ops = [{"action": "create_component", "name": "Cockpit_Main"}]
        res = edit_assembly_logic(ops, "en")

        self.assertIn("Error: Some assembly operations failed:", res)
        self.assertIn("ERR_VERIFICATION_FAILED", res)

    @patch('core.bridge.requests.post')
    def test_edit_assembly_reports_rename_component_errors(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["rename_component:ERR_NEW_NAME_REQUIRED"]}
        mock_post.return_value = mock_response

        ops = [{"action": "rename_component", "target_component_path": "Root/Frame/Arm"}]
        res = edit_assembly_logic(ops, "en")

        self.assertIn("Error: Some assembly operations failed:", res)
        self.assertIn("new_name is required", res)

    @patch('core.bridge.requests.post')
    def test_edit_assembly_reports_move_component_errors(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["move_component:ERR_COMPONENT"]}
        mock_post.return_value = mock_response

        ops = [{"action": "move_component", "target_component_path": "Root/Frame/Missing", "x": 1}]
        res = edit_assembly_logic(ops, "en")

        self.assertIn("Error: Some assembly operations failed:", res)
        self.assertIn("component not found", res.lower())

if __name__ == '__main__':
    unittest.main()
