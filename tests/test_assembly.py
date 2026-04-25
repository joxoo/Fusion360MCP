import unittest
from unittest.mock import MagicMock, patch
from core.bridge import execute_fusion_script
from modules.assembly import create_joint_logic

class TestAssembly(unittest.TestCase):
    @patch('core.bridge.requests.post')
    def test_create_joint_payload(self, mock_post):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        # Execute logic
        res = create_joint_logic("Comp1", "Comp2", "Revolute", "en")
        
        # Verify
        self.assertIn("Joint (Revolute) created.", res)
        sent_payload = mock_post.call_args[1]['json']
        params = sent_payload['payload']['params']
        self.assertEqual(params['c1'], "Comp1")
        self.assertEqual(params['c2'], "Comp2")
        self.assertEqual(params['type'], "Revolute")

if __name__ == '__main__':
    unittest.main()
