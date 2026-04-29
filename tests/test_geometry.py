import unittest
from unittest.mock import MagicMock, patch
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

if __name__ == '__main__':
    unittest.main()
