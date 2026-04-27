import unittest
from unittest.mock import MagicMock, patch
from modules.analysis import (
    capture_view_logic,
    analyze_bodies_logic,
    check_interference_logic,
    create_draft_analysis_logic,
    get_volumetric_properties_logic,
    get_bounding_box_logic,
    validate_model_logic,
    get_scene_map_logic
)

class TestAnalysis(unittest.TestCase):
    @patch('modules.analysis.execute_fusion_script')
    def test_get_scene_map_params(self, mock_exec):
        mock_data = '[{"name": "Body1", "center": {"x": 0, "y": 0, "z": 0}, "bbox": {"size": {"l": 10, "w": 10, "h": 10}}}]'
        mock_exec.return_value = {"status": "success", "data": [mock_data]}
        res = get_scene_map_logic("en")
        self.assertEqual(res, mock_data)

    @patch('modules.analysis.execute_fusion_script')
    def test_validate_model_success(self, mock_exec):
        mock_report = '{"body_count": 1, "is_single_solid": true, "interferences": 0, "manifold_issues": []}'
        mock_exec.return_value = {"status": "success", "data": [mock_report]}
        res = validate_model_logic("en")
        self.assertIn("Model Validation Report:", res)
        self.assertIn("Body Count: 1", res)
        self.assertIn("Ready for Print", res)

    @patch('modules.analysis.execute_fusion_script')
    def test_validate_model_warning(self, mock_exec):
        mock_report = '{"body_count": 2, "is_single_solid": false, "interferences": 1, "manifold_issues": ["Body2 is surface"]}'
        mock_exec.return_value = {"status": "success", "data": [mock_report]}
        res = validate_model_logic("en")
        self.assertIn("Warning: Multiple bodies detected", res)
        self.assertIn("Interferences: 1", res)
        self.assertIn("Manifold Issues: Body2 is surface", res)
        self.assertIn("Action Required", res)

    @patch('modules.analysis.execute_fusion_script')
    def test_get_volumetric_properties_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ['{"mass_kg": 0.5, "volume_cm3": 100}']}
        res = get_volumetric_properties_logic("Body1", "en")
        self.assertIn('"mass_kg": 0.5', res)

    @patch('modules.analysis.execute_fusion_script')
    def test_get_bounding_box_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ['{"length": 10.0, "width": 5.0}']}
        res = get_bounding_box_logic("Body1", "en")
        self.assertIn('"length": 10.0', res)

    @patch('modules.analysis.execute_fusion_script')
    def test_check_interference_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["0"]}
        res = check_interference_logic(["Body1", "Body2"], False, "en")
        self.assertEqual(res, "No interferences detected. The assembly fits perfectly.")
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['body_names'], ["Body1", "Body2"])

    @patch('modules.analysis.execute_fusion_script')
    def test_check_interference_warning(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["3"]}
        res = check_interference_logic(["Body1", "Body2"], False, "en")
        self.assertIn("Warning: Found 3 interferences", res)

    @patch('modules.analysis.execute_fusion_script')
    def test_create_draft_analysis_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["Draft1"]}
        res = create_draft_analysis_logic("Body1", 1.0, 10.0, "en")
        self.assertIn("Draft analysis 'Draft1' created", res)
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['body'], "Body1")
        self.assertEqual(params['min_angle'], 1.0)

if __name__ == '__main__':
    unittest.main()
