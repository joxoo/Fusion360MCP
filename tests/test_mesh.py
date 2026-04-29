import unittest
from unittest.mock import MagicMock, patch
from modules.mesh import edit_mesh_logic
from core.utils import load_i18n

class TestMesh(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_edit_mesh_batch(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["remesh:OK"]}
        mock_post.return_value = mock_response

        ops = [{"action": "remesh", "body": "Mesh1", "density": 0.8}]
        res = edit_mesh_logic(ops, "en")
        self.assertEqual(res, "Mesh updated successfully.")

if __name__ == '__main__':
    unittest.main()
