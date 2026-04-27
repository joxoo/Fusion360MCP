import unittest
from unittest.mock import MagicMock, patch
from modules.mesh import (
    import_mesh_logic,
    tessellate_body_logic,
    generate_face_groups_logic,
    repair_mesh_logic,
    convert_mesh_logic,
    remesh_body_logic,
    smooth_mesh_logic,
    mesh_plane_cut_logic
)

class TestMesh(unittest.TestCase):
    @patch('modules.mesh.execute_fusion_script')
    def test_remesh_body_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = remesh_body_logic("Mesh1", 0.7, "en")
        self.assertIn("successfully remeshed", res)
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['density'], 0.7)

    @patch('modules.mesh.execute_fusion_script')
    def test_smooth_mesh_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = smooth_mesh_logic("Mesh1", 0.8, "en")
        self.assertIn("successfully smoothed", res)
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['smoothing'], 0.8)

    @patch('modules.mesh.execute_fusion_script')
    def test_mesh_plane_cut_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = mesh_plane_cut_logic("Mesh1", "XZ", "MeshFill", "en")
        self.assertIn("successfully cut using XZ plane", res)
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['plane'], "XZ")

    @patch('modules.mesh.execute_fusion_script')
    def test_import_mesh_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = import_mesh_logic("/path/to/mesh.stl", "en")
        self.assertIn("successfully imported", res)

    @patch('modules.mesh.execute_fusion_script')
    def test_tessellate_body_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = tessellate_body_logic("B1", "en")
        self.assertIn("successfully tessellated", res)
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['body'], "B1")

    @patch('modules.mesh.execute_fusion_script')
    def test_generate_face_groups_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = generate_face_groups_logic("Mesh1", True, "en")
        self.assertEqual(res, "Face groups generated on 'Mesh1'.")
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['type'], 1)

    @patch('modules.mesh.execute_fusion_script')
    def test_repair_mesh_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = repair_mesh_logic("Mesh1", "infoTypeDefault", "en")
        self.assertIn("repair command executed", res)
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['repair_type'], "infoTypeDefault")

    @patch('modules.mesh.execute_fusion_script')
    def test_convert_mesh_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = convert_mesh_logic("Mesh1", "infoPrismatic", "en")
        self.assertIn("successfully converted to solid", res)
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['conv_type'], "infoPrismatic")

if __name__ == '__main__':
    unittest.main()
