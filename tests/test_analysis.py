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
        self.assertIn("elif action == 'get_feature_history':", script)
        self.assertIn('"feature_type": feature_type', script)
        self.assertIn('"is_rolled_back": idx >= timeline.markerPosition', script)
        self.assertIn('results = {"body_count": 0, "brep_count": 0, "mesh_count": 0, "sketch_count": 0, "bodies": [], "sketches": [], "manifold_issues": []}', script)
        self.assertIn('results["body_count"] = results["brep_count"]', script)
        self.assertIn('results["sketch_count"] = len(results["sketches"])', script)
        self.assertIn('collect_validation(root, results)', script)
        self.assertIn('collect_scene_map(root, scene_map)', script)
        self.assertIn('"component_path": comp_path', script)
        self.assertIn('"body_ref": make_body_ref', script)
        self.assertIn('"component_ref": make_component_ref(comp)', script)
        self.assertIn('get_component_path(get_owner_component(target))', script)
        self.assertIn('"sketch_ref": {"sketch": sketch.name, "component_path": component_path}', script)
        self.assertIn('"curve_ref": {"sketch": sketch_name, "component_path": component_path, "curve_index": curve_index}', script)
        self.assertIn('"constraint_ref": {"sketch": sketch_name, "component_path": component_path, "constraint_index": constraint_index}', script)
        self.assertIn('"dimension_ref": {"sketch": sketch_name, "component_path": component_path, "dimension_index": dimension_index}', script)
        self.assertIn('"constraint_count": len(constraints)', script)
        self.assertIn('"dimension_count": len(dimensions)', script)

if __name__ == '__main__':
    unittest.main()
