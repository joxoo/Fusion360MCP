import unittest
from unittest.mock import MagicMock, patch
from core.bridge import execute_fusion_script
from modules.geometry import create_chamfer_logic, create_shell_logic
from modules.mechanical import create_bolt_logic

class TestGeometryExtended(unittest.TestCase):
    @patch('core.bridge.requests.post')
    def test_create_chamfer_payload(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = create_chamfer_logic("MyBody", 0.5, "en")
        self.assertEqual(res, "Chamfer created.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['dist'], 0.5)

    @patch('core.bridge.requests.post')
    def test_bolt_numeric_size(self, mock_post):
        # Finding 1 Check: Verify that bolt logic sends numeric string resolution
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["10.0"]}
        mock_post.return_value = mock_response

        create_bolt_logic(10, 5, True, "en")
        script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn('dia_val = float(params[\'dia_mm\'])', script)
        self.assertIn('adsk.fusion.ThreadInfo.create', script)

if __name__ == '__main__':
    unittest.main()
