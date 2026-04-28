import unittest
from unittest.mock import MagicMock, patch
from modules.sketch import create_sketch_logic

from core.utils import load_i18n

class TestCreateSketch(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_create_sketch_on_plane(self, mock_post):
        """Verify standard sketch creation on a plane."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Sketch1"]}
        mock_post.return_value = mock_response

        res = create_sketch_logic("XY", "MySketch", "en")
        self.assertTrue("Sketch1" in res or "sketch_created" in res)
        
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['plane'], "XY")
        self.assertEqual(params['name'], "MySketch")
        self.assertIsNone(params.get('body'))
        self.assertIsNone(params.get('component_name'))

    @patch('core.bridge.requests.post')
    def test_create_sketch_on_face(self, mock_post):
        """Verify sketch creation on a body face."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["FaceSketch"]}
        mock_post.return_value = mock_response

        res = create_sketch_logic(name="FaceSketch", body_name="Medal", face_index=5)
        self.assertTrue("FaceSketch" in res or "sketch_created" in res)
        
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['body'], "Medal")
        self.assertEqual(params['face_index'], 5)

    @patch('core.bridge.requests.post')
    def test_create_sketch_with_component_scope(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["ScopedSketch"]}
        mock_post.return_value = mock_response

        res = create_sketch_logic("YZ", "ScopedSketch", "en", component_path="Root/SubAssembly")
        self.assertTrue("ScopedSketch" in res or "sketch_created" in res)

        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['component_path'], "Root/SubAssembly")

if __name__ == '__main__':
    unittest.main()
