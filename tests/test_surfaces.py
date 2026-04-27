import unittest
from unittest.mock import MagicMock, patch
from modules.surfaces import (
    create_surface_patch_logic,
    offset_surface_logic,
    stitch_surfaces_logic,
    thicken_surface_logic,
    create_surface_cylinder_logic,
    create_surface_sphere_logic,
    create_surface_torus_logic,
    trim_surface_logic,
    extend_surface_logic,
    reverse_surface_normal_logic
)

class TestSurfaces(unittest.TestCase):
    @patch('modules.surfaces.execute_fusion_script')
    def test_create_surface_patch_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["Patch1"]}
        res = create_surface_patch_logic("S1", "en")
        self.assertEqual(res, "Surface patch created: Patch1")

    @patch('modules.surfaces.execute_fusion_script')
    def test_trim_surface_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = trim_surface_logic("Body1", "ToolSketch", "en")
        self.assertEqual(res, "Surface 'Body1' trimmed successfully.")
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['body'], "Body1")
        self.assertEqual(params['tool_sketch'], "ToolSketch")

    @patch('modules.surfaces.execute_fusion_script')
    def test_extend_surface_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = extend_surface_logic("Body1", 2.0, "en")
        self.assertEqual(res, "Surface 'Body1' extended by 2.0 cm.")

    @patch('modules.surfaces.execute_fusion_script')
    def test_reverse_surface_normal_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = reverse_surface_normal_logic("Body1", "en")
        self.assertEqual(res, "Normal direction of 'Body1' reversed.")

    @patch('modules.surfaces.execute_fusion_script')
    def test_offset_surface_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["Offset1"]}
        res = offset_surface_logic("Body1", 1.0, "en")
        self.assertEqual(res, "Offset surface created: Offset1")

    @patch('modules.surfaces.execute_fusion_script')
    def test_stitch_surfaces_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["Solid1"]}
        res = stitch_surfaces_logic(["S1", "S2"], 0.1, "en")
        self.assertIn("Surfaces stitched successfully", res)

if __name__ == '__main__':
    unittest.main()
