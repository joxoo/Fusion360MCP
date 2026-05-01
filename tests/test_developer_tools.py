import unittest
from unittest.mock import MagicMock, patch
from modules.geometry import (
    apply_3d_features_logic,
    execute_python_script_logic
)
from core.utils import load_i18n
from modules.geometry_scripts import build_apply_3d_features_script

class TestDeveloperTools(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_execute_python_script_tool(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["42"]}
        mock_post.return_value = mock_response

        res = execute_python_script_logic("returnValue.append(42)", {})
        self.assertEqual(res, "Script executed successfully. Result: 42")

    @patch('core.bridge.requests.post')
    def test_apply_3d_features_execute_python_action(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["execute_python:OK:ResultVal"]}
        mock_post.return_value = mock_response

        ops = [{"action": "execute_python", "script": "returnValue.append('ResultVal')"}]
        res = apply_3d_features_logic(ops, "en")
        self.assertEqual(res, "3D geometry updated successfully.")

    @patch('core.bridge.requests.post')
    def test_apply_3d_features_pattern_feature_action(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["pattern_feature:OK"]}
        mock_post.return_value = mock_response

        ops = [{"action": "pattern_feature", "feature_name": "Extrude1", "axis": "Z", "count": 10}]
        res = apply_3d_features_logic(ops, "en")
        self.assertEqual(res, "3D geometry updated successfully.")

    @patch('core.bridge.requests.post')
    def test_apply_3d_features_move_body_rotation(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["move_body:OK"]}
        mock_post.return_value = mock_response

        ops = [{"action": "move_body", "body": "Body1", "rx": 0.785}]
        res = apply_3d_features_logic(ops, "en")
        self.assertEqual(res, "3D geometry updated successfully.")

    @patch('core.bridge.requests.post')
    def test_apply_3d_features_mirror_feature(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["mirror_feature:OK"]}
        mock_post.return_value = mock_response

        ops = [{"action": "mirror_feature", "feature_name": "Extrude1", "plane": "XZ"}]
        res = apply_3d_features_logic(ops, "en")
        self.assertEqual(res, "3D geometry updated successfully.")

    @patch('core.bridge.requests.post')
    def test_apply_3d_features_create_thread(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["create_thread:OK"]}
        mock_post.return_value = mock_response

        ops = [{"action": "create_thread", "body": "Cyl1", "is_modeled": True}]
        res = apply_3d_features_logic(ops, "en")
        self.assertEqual(res, "3D geometry updated successfully.")

    def test_script_contains_new_actions(self):
        script = build_apply_3d_features_script()
        self.assertIn("elif action == 'execute_python':", script)
        self.assertIn("elif action == 'pattern_feature':", script)
        self.assertIn("elif action == 'rectangular_pattern_feature':", script)
        self.assertIn("elif action == 'mirror_feature':", script)
        self.assertIn("elif action == 'create_construction_plane':", script)
        self.assertIn("elif action == 'create_construction_axis':", script)
        self.assertIn("elif action == 'create_thread':", script)
        self.assertIn("elif action == 'create_coil':", script)
        self.assertIn("elif action == 'select_by_property':", script)
        self.assertIn("elif action == 'align_to_normal':", script)
        self.assertIn("elif action == 'apply_taper_to_extrude':", script)
        self.assertIn("if any(k in op for k in ['rx', 'ry', 'rz']):", script)
        self.assertIn("rot.setToRotation(op['rx']", script)
        self.assertIn("patterns = feature_owner.features.circularPatternFeatures", script)

if __name__ == '__main__':
    unittest.main()
