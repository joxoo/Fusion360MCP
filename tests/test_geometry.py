import unittest
from unittest.mock import MagicMock, patch
from modules.geometry import (
    apply_3d_features_logic,
    create_box_logic,
    delete_face_logic
)
from core.utils import load_i18n

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

if __name__ == '__main__':
    unittest.main()
