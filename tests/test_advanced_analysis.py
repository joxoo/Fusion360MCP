import unittest
from unittest.mock import MagicMock, patch
from modules.analysis import analyze_design_logic, capture_side_logic
from core.utils import load_i18n
from modules.analysis_scripts import build_analyze_design_script

class TestAdvancedAnalysis(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_analyze_design_interference_check(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ['[{"body1": "A", "body2": "B", "volume_cm3": 0.5}]']}
        mock_post.return_value = mock_response

        res = analyze_design_logic(action="interference_check", lang="en")
        self.assertIn('"body1": "A"', res)
        self.assertIn('"volume_cm3": 0.5', res)

    @patch('core.bridge.requests.post')
    def test_capture_side(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["BASE64_IMAGE_DATA"]}
        mock_post.return_value = mock_response

        res = capture_side_logic("en")
        self.assertEqual(res, "BASE64_IMAGE_DATA")
        
        # Verify the correct action was sent to the script
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['action'], "capture_side")

    def test_analyze_design_script_has_new_actions(self):
        script = build_analyze_design_script()
        self.assertIn("elif action == 'interference_check':", script)
        self.assertIn("design.analyzeInterference(input_set)", script)
        self.assertIn("elif action == 'capture_side':", script)
        self.assertIn("view.goRight()", script)
        self.assertIn("view.camera.cameraType = adsk.core.CameraTypes.OrthographicCameraType", script)

if __name__ == '__main__':
    unittest.main()
