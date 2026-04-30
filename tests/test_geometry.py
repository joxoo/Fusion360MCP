import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from modules.geometry import (
    apply_3d_features_logic,
    create_box_logic,
    delete_face_logic
)
from core.utils import load_i18n
from modules.geometry_scripts import build_apply_3d_features_script, build_create_box_script

class TestGeometry(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_apply_3d_features_batch(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["extrude:OK,fillet:OK"]}
        mock_post.return_value = mock_response

        ops = [
            {"action": "extrude", "sketch": "Sketch1", "dist": 10},
            {"action": "fillet", "body": "Body1", "r": 2}
        ]
        res = apply_3d_features_logic(ops, "en")
        self.assertEqual(res, "3D geometry updated successfully.")

    @patch('core.bridge.requests.post')
    def test_create_box_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["MyBox"]}
        mock_post.return_value = mock_response

        res = create_box_logic(10, 10, 10, "MyBox", 0, 0, 0, "NewBody", 0, "en")
        self.assertEqual(res, "Box 'MyBox' created.")

    @patch('core.bridge.requests.post')
    def test_delete_face_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = delete_face_logic("Body1", 2, "en")
        self.assertEqual(res, "Face 2 of 'Body1' deleted.")

    def test_apply_3d_features_script_uses_plain_results_and_verification(self):
        script = build_apply_3d_features_script()
        self.assertIn('results.append(f"{action}:ERR_VERIFICATION_FAILED")', script)
        self.assertIn('returnValue.append(",".join(results) if results else "OK")', script)
        self.assertNotIn("TRACE:", script)
        self.assertIn("delete_body", script)
        self.assertIn("rename_body", script)
        self.assertIn("move_body_absolute", script)
        self.assertIn("scale_body", script)
        self.assertIn("shell", script)
        self.assertIn("split_body", script)
        self.assertIn("delete_face", script)
        self.assertIn("offset_face", script)
        self.assertIn("move_face", script)
        self.assertIn("edit_feature", script)
        self.assertIn("delete_feature", script)
        self.assertIn("find_named_feature", script)
        self.assertIn("body_in_requested_scope", script)
        self.assertIn("deleted = target.deleteMe()", script)
        self.assertIn("ERR_DELETE_FAILED", script)
        self.assertIn("Always provide semantic body names", Path("docs/AI_USAGE.md").read_text(encoding="utf-8"))
        self.assertIn("pick_body_name(op, 'Box')", script)
        self.assertIn("pick_body_name(op, 'Cylinder')", script)
        self.assertIn("pick_body_name(op, 'Sphere')", script)
        self.assertIn("body_lookup_error", script)
        self.assertIn("suggestions=", script)
        self.assertIn("' | '.join(suggestions)", script)
        self.assertIn("collect_body_refs", script)
        self.assertIn("'label': f\"{body.name} @ {comp_path}\"", script)

    def test_apply_3d_features_script_supports_cylinder_alias_fields(self):
        script = build_apply_3d_features_script()
        self.assertIn("center_coords = op.get('center', [0,0,0])", script)
        self.assertIn("op.get('x', center_coords[0])", script)
        self.assertIn("h = float(op.get('height', op.get('h', 0)))", script)

    def test_apply_3d_features_script_supports_box_height_alias(self):
        script = build_apply_3d_features_script()
        self.assertIn("h = float(op.get('height', op.get('h', 0)))", script)
        self.assertIn("createByReal(h), 3", script)

    def test_create_box_script_verifies_created_body(self):
        script = build_create_box_script()
        self.assertIn("if find_body_recursive(root, body.name):", script)
        self.assertIn('returnValue.append("ERR_VERIFICATION_FAILED")', script)

    @patch('core.bridge.requests.post')
    def test_apply_3d_features_reports_body_rename_errors(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["rename_body:ERR_NEW_NAME_REQUIRED"]}
        mock_post.return_value = mock_response

        ops = [{"action": "rename_body", "body": "Body1"}]
        res = apply_3d_features_logic(ops, "en")

        self.assertIn("Error: Some operations failed:", res)
        self.assertIn("new_name is required", res)

    @patch('core.bridge.requests.post')
    def test_apply_3d_features_preserves_body_suggestions(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": ["rename_body:ERR_BODY_NOT_FOUND (requested='Körper1'; suggestions=Cockpit_Floor @ Root/Cockpit:1 | Cockpit_Walls @ Root/Cockpit:1)"]
        }
        mock_post.return_value = mock_response

        ops = [{"action": "rename_body", "body": "Körper1", "new_name": "Cockpit_Walls"}]
        res = apply_3d_features_logic(ops, "en")

        self.assertIn("body_not_found", res)
        self.assertIn("Cockpit_Floor", res)
        self.assertIn("Cockpit_Walls", res)
        self.assertIn("Root/Cockpit:1", res)

    @patch('core.bridge.requests.post')
    def test_apply_3d_features_reports_feature_and_face_errors(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": ["edit_feature:ERR_FEATURE_NOT_FOUND,delete_face:ERR_FACE_INDEX"]
        }
        mock_post.return_value = mock_response

        ops = [
            {"action": "edit_feature", "feature_name": "MissingExtrude"},
            {"action": "delete_face", "body": "Body1", "face_index": 99},
        ]
        res = apply_3d_features_logic(ops, "en")

        self.assertIn("feature_not_found", res)
        self.assertIn("face_index is out of range", res)

    @patch('core.bridge.requests.post')
    def test_apply_3d_features_reports_delete_failures(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": ["delete_body:ERR_DELETE_FAILED"]
        }
        mock_post.return_value = mock_response

        ops = [{"action": "delete_body", "body": "Canopy_Glass_Top", "component_path": "Root/Cockpit_v2:1"}]
        res = apply_3d_features_logic(ops, "en")

        self.assertIn("body delete operation failed", res)

if __name__ == '__main__':
    unittest.main()
