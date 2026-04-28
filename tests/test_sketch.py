import unittest
from unittest.mock import MagicMock, patch
from modules.sketch import (
    create_sketch_logic,
    draw_line_logic,
    draw_rectangle_logic,
    create_sketch_circular_pattern_logic
)

from core.utils import load_i18n

class TestSketch(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_create_sketch_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["MySketch"]}
        mock_post.return_value = mock_response

        res = create_sketch_logic("XZ", "MySketch", "en")
        
        self.assertEqual(res, "Sketch 'MySketch' created.")
        sent_payload = mock_post.call_args[1]['json']
        params = sent_payload['payload']['params']
        self.assertEqual(params['plane'], "XZ")
        self.assertEqual(params['name'], "MySketch")
        script = sent_payload['payload']['script']
        self.assertIn("resolve_sketch_creation_context(params)", script)
        self.assertIn("owner_comp.sketches.add(target_plane)", script)

    @patch('core.bridge.requests.post')
    def test_draw_line_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = draw_line_logic("MySketch", 0, 0, 10, 10, "en")
        
        self.assertEqual(res, "Line drawn.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['sketch'], "MySketch")
        self.assertEqual(params['x1'], 0)
        self.assertEqual(params['x2'], 10)
        script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("s.sketchCurves.sketchLines.addByTwoPoints(p1, p2)", script)

    @patch('core.bridge.requests.post')
    def test_draw_rectangle_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = draw_rectangle_logic("MySketch", 0, 0, 5, 5, "en")
        
        self.assertEqual(res, "Rectangle drawn.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['x2'], 5)
        script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("s.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)", script)

    @patch('core.bridge.requests.post')
    def test_circular_pattern_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = create_sketch_circular_pattern_logic("MySketch", 0, 0, 4, "en")
        
        self.assertEqual(res, "Sketch pattern created.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['count'], 4)
        script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("constraints.addCircularPattern(pattern_input)", script)

    @patch('core.bridge.requests.post')
    def test_handle_sketch_not_found(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["ERR_SKETCH"]}
        mock_post.return_value = mock_response

        res = draw_line_logic("NonExistent", 0, 0, 1, 1, "en")
        self.assertEqual(res, "Sketch or profile not found.")

if __name__ == '__main__':
    unittest.main()
