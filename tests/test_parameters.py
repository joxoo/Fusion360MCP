import unittest
from unittest.mock import MagicMock, patch
from core.bridge import execute_fusion_script
from modules.parameters import manage_parameter_logic

class TestParameters(unittest.TestCase):
    @patch('core.bridge.requests.post')
    def test_update_parameter_payload(self, mock_post):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["UPDATED"]}
        mock_post.return_value = mock_response

        # Execute logic (Signature: name, expression, unit, comment, lang)
        res = manage_parameter_logic("Length", "10 cm", "mm", "", "en")
        
        # Verify
        self.assertIn("Parameter 'Length' updated.", res)
        sent_payload = mock_post.call_args[1]['json']
        params = sent_payload['payload']['params']
        self.assertEqual(params['name'], "Length")
        self.assertEqual(params['expr'], "10 cm")

if __name__ == '__main__':
    unittest.main()
