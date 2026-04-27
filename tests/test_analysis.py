import unittest
from unittest.mock import MagicMock, patch
from modules.analysis import (
    capture_view_logic,
    analyze_bodies_logic,
    check_interference_logic,
    create_draft_analysis_logic,
    get_volumetric_properties_logic,
    get_bounding_box_logic
)

class TestAnalysis(unittest.TestCase):
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
