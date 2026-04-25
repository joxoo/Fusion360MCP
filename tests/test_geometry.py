import unittest
from unittest.mock import MagicMock, patch
from core.bridge import execute_fusion_script
from modules.geometry import create_box_logic

class TestGeometry(unittest.TestCase):
    @patch('core.bridge.requests.post')
    def test_create_box_params(self, mock_post):
        # Configure mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["MyBox"]}
        mock_post.return_value = mock_response

        # Execute logic (Signature: l, w, h, name, x, y, z, op, taper, lang)
        res = create_box_logic(10, 20, 5, "MyBox", 1, 2, 3, "NewBody", 0, "en")
        
        # Verify
        self.assertEqual(res, "Box 'MyBox' created.")
        sent_payload = mock_post.call_args[1]['json']
        params = sent_payload['payload']['params']
        self.assertEqual(params['l'], 10)
        self.assertEqual(params['x'], 1)

if __name__ == '__main__':
    unittest.main()
