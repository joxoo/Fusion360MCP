import unittest
from unittest.mock import MagicMock, patch
from core.bridge import execute_fusion_script, FusionBridgeError

class TestBridge(unittest.TestCase):
    @patch('core.bridge.requests.post')
    def test_execute_fusion_script_success(self, mock_post):
        # Configure mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Test Result"]}
        mock_post.return_value = mock_response

        res = execute_fusion_script("print('Hello')", {"val": 1})
        
        self.assertEqual(res["data"][0], "Test Result")
        # Check payload
        sent_payload = mock_post.call_args[1]['json']
        self.assertIn("print('Hello')", sent_payload['payload']['script'])

    @patch('core.bridge.requests.post')
    def test_execute_fusion_script_error(self, mock_post):
        # Configure mock error response from bridge
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "error", "message": "Fusion API Error"}
        mock_post.return_value = mock_response

        with self.assertRaises(FusionBridgeError) as cm:
            execute_fusion_script("invalid code")
        
        self.assertEqual(str(cm.exception), "Fusion API Error")

if __name__ == '__main__':
    unittest.main()
