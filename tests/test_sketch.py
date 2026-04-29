import unittest
from unittest.mock import MagicMock, patch
from modules.sketch import (
    create_sketch_logic,
    edit_sketch_logic,
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

    @patch('core.bridge.requests.post')
    def test_edit_sketch_batch(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["draw_line:OK"]}
        mock_post.return_value = mock_response

        ops = [{"action": "draw_line", "x1": 0, "y1": 0, "x2": 10, "y2": 10}]
        res = edit_sketch_logic("MySketch", ops, "en")
        
        self.assertEqual(res, "Sketch 'MySketch' updated successfully.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['sketch'], "MySketch")
        self.assertEqual(params['operations'][0]['action'], "draw_line")
        script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("for op in params.get('operations', []):", script)

if __name__ == '__main__':
    unittest.main()
