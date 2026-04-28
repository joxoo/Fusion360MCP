import unittest
from unittest.mock import MagicMock, patch
from modules.advanced_geometry import (
    create_loft_logic,
    create_sweep_logic,
    measure_distance_logic,
    get_center_of_mass_logic,
    apply_appearance_logic
)
from core.utils import load_i18n

class TestAdvancedGeometry(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_create_loft_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Loft1"]}
        mock_post.return_value = mock_response

        res = create_loft_logic(["S1", "S2"], "en")
        
        self.assertEqual(res, "Loft created: Loft1")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['sketch_names'], ["S1", "S2"])
        script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("loft_in.loftSections.add(p)", script)
        self.assertIn("resolve_multi_sketch_context(", script)

    @patch('core.bridge.requests.post')
    def test_create_sweep_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Sweep1"]}
        mock_post.return_value = mock_response

        res = create_sweep_logic("Prof", "Path", "en")
        
        self.assertEqual(res, "Sweep created: Sweep1")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['profile_sketch'], "Prof")
        self.assertEqual(params['path_sketch'], "Path")
        script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("resolve_sketch_context(", script)

    @patch('core.bridge.requests.post')
    def test_create_loft_owner_mismatch(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["ERR_OWNER_MISMATCH"]}
        mock_post.return_value = mock_response

        res = create_loft_logic(["S1", "S2"], "en")
        self.assertEqual(res, "Entities belong to different components. Cross-component operations are limited.")

    @patch('core.bridge.requests.post')
    def test_create_sweep_component_scope(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Sweep1"]}
        mock_post.return_value = mock_response

        res = create_sweep_logic("Prof", "Path", "en", component_path="Root/Assembly")
        self.assertEqual(res, "Sweep created: Sweep1")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['component_path'], "Root/Assembly")

    @patch('core.bridge.requests.post')
    def test_measure_distance_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["5.2345"]}
        mock_post.return_value = mock_response

        res = measure_distance_logic("Body1", "Body2", "en")
        self.assertEqual(res, "Distance: 5.2345 cm")
        
        script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("meas.measure(b1, b2)", script)

    @patch('core.bridge.requests.post')
    def test_get_center_of_mass_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["1.0,2.0,3.0"]}
        mock_post.return_value = mock_response

        res = get_center_of_mass_logic("Body1", "en")
        self.assertEqual(res, "Center of Mass (X,Y,Z): 1.0,2.0,3.0")

    @patch('core.bridge.requests.post')
    def test_export_step_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Exported to path/test.step"]}
        mock_post.return_value = mock_response

        from modules.advanced_geometry import export_step_logic
        res = export_step_logic("test", "en")
        self.assertIn("Exported to", res)
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['filename'], "test")

if __name__ == '__main__':
    unittest.main()
