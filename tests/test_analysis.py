import unittest
from unittest.mock import MagicMock, patch
from modules.analysis import analyze_design_logic
from core.utils import load_i18n
from modules.analysis_scripts import build_analyze_design_script

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_analyze_design_validate(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ['{"body_count": 1}']}
        mock_post.return_value = mock_response

        res = analyze_design_logic("validate", "en")
        self.assertEqual(res, '{"body_count": 1}')

    def test_analyze_design_script_validate_keeps_compat_and_recursion(self):
        script = build_analyze_design_script()
        self.assertIn('results = {"body_count": 0, "brep_count": 0, "mesh_count": 0, "bodies": [], "manifold_issues": []}', script)
        self.assertIn('results["body_count"] = results["brep_count"]', script)
        self.assertIn('collect_validation(root, results)', script)
        self.assertIn('collect_scene_map(root, scene_map)', script)

if __name__ == '__main__':
    unittest.main()
