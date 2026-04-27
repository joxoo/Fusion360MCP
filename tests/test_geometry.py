import unittest
from unittest.mock import MagicMock, patch
from modules.geometry import (
    create_box_logic,
    create_hole_logic,
    create_cylinder_logic,
    create_sphere_logic,
    create_torus_logic,
    create_coil_logic,
    create_pipe_logic,
    create_revolve_logic,
    create_boundary_fill_logic,
    create_hole_advanced_logic,
    create_pattern_on_path_logic,
    mirror_features_logic,
    combine_bodies_logic,
    split_body_logic,
    scale_body_logic,
    move_body_logic,
    create_plastic_rib_logic,
    create_plastic_web_logic,
    create_plastic_boss_logic,
    create_snap_fit_logic,
    delete_face_logic,
    offset_face_logic,
    move_face_logic
)

class TestGeometry(unittest.TestCase):
    @patch('core.bridge.requests.post')
    def test_delete_face_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = delete_face_logic("Body1", 2, "en")
        self.assertEqual(res, "Face 2 of 'Body1' deleted.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['face_index'], 2)

    @patch('core.bridge.requests.post')
    def test_offset_face_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = offset_face_logic("Body1", 1.5, 0, "en")
        self.assertEqual(res, "Face 0 of 'Body1' offset by 1.5 cm.")

    @patch('core.bridge.requests.post')
    def test_move_face_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = move_face_logic("Body1", 0, 0, 5, 0, "en")
        self.assertEqual(res, "Face 0 of 'Body1' moved.")

    @patch('core.bridge.requests.post')
    def test_create_plastic_rib_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Rib1"]}
        mock_post.return_value = mock_response

        res = create_plastic_rib_logic("RibPath", 0.2, "en")
        self.assertEqual(res, "Plastic rib 'Rib1' created.")

    @patch('core.bridge.requests.post')
    def test_combine_bodies_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = combine_bodies_logic("Target", ["Tool1", "Tool2"], "Cut", "en")
        self.assertEqual(res, "Bodies successfully combined.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['operation'], "Cut")

    @patch('core.bridge.requests.post')
    def test_split_body_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = split_body_logic("Body1", "XY", "en")
        self.assertEqual(res, "Body successfully split.")

    @patch('core.bridge.requests.post')
    def test_split_body_tool_not_found(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["ERR_TOOL"]}
        mock_post.return_value = mock_response

        res = split_body_logic("Body1", "MissingPlane", "en")
        self.assertEqual(res, "Error: Splitting tool 'MissingPlane' not found.")

    @patch('core.bridge.requests.post')
    def test_scale_body_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = scale_body_logic("Body1", 2.0, "en")
        self.assertEqual(res, "Body 'Body1' scaled by factor 2.0.")

    @patch('core.bridge.requests.post')
    def test_move_body_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = move_body_logic("Body1", 5, 0, 0, 45, "en")
        self.assertEqual(res, "Body 'Body1' moved.")

    @patch('core.bridge.requests.post')
    def test_create_plastic_boss_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Boss1"]}
        mock_post.return_value = mock_response

        res = create_plastic_boss_logic("Boss_Positions", True, "en")
        self.assertEqual(res, "Plastic boss 'Boss1' created.")

    @patch('core.bridge.requests.post')
    def test_create_snap_fit_unsupported(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["ERR_UNSUPPORTED"]}
        mock_post.return_value = mock_response

        res = create_snap_fit_logic("SnapFit_Path", "en")
        self.assertEqual(res, "Error: Snap Fit is not exposed by the current Fusion API/runtime.")

    @patch('core.bridge.requests.post')
    def test_create_box_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["MyBox"]}
        mock_post.return_value = mock_response

        res = create_box_logic(10, 10, 10, "MyBox", 0, 0, 0, "NewBody", 0, "en")
        self.assertEqual(res, "Box 'MyBox' created.")

if __name__ == '__main__':
    unittest.main()
