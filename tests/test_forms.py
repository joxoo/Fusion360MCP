import unittest
from unittest.mock import MagicMock, patch
from modules.forms import (
    create_form_box_logic,
    create_form_sphere_logic,
    create_form_extrude_logic,
    create_form_revolve_logic,
    create_form_sweep_logic,
    create_form_loft_logic,
    insert_form_edge_logic,
    subdivide_form_face_logic,
    create_form_crease_logic,
    create_form_mirror_internal_logic,
    clear_form_symmetry_logic,
    set_form_display_mode_logic,
    fill_form_hole_logic,
    convert_form_logic
)

class TestForms(unittest.TestCase):
    @patch('modules.forms.execute_fusion_script')
    def test_create_form_extrude_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["FormBody1"]}
        res = create_form_extrude_logic("S1", 5.0, False, "en")
        self.assertEqual(res, "Form extrude created: FormBody1")
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['sketch'], "S1")
        self.assertEqual(params['dist'], 5.0)

    @patch('modules.forms.execute_fusion_script')
    def test_set_form_display_mode_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = set_form_display_mode_logic("Form1", "Box", "en")
        self.assertEqual(res, "Display mode for 'Form1' set to Box.")
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['mode'], "Box")

    @patch('modules.forms.execute_fusion_script')
    def test_fill_form_hole_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = fill_form_hole_logic("Form1", "en")
        self.assertEqual(res, "Hole filled in 'Form1'.")

    @patch('modules.forms.execute_fusion_script')
    def test_convert_form_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = convert_form_logic("Form1", "en")
        self.assertEqual(res, "Form 'Form1' successfully converted to solid.")

    @patch('modules.forms.execute_fusion_script')
    def test_create_form_mirror_internal_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = create_form_mirror_internal_logic("Form1", "en")
        self.assertEqual(res, "Internal mirror symmetry created in 'Form1'.")

    @patch('modules.forms.execute_fusion_script')
    def test_insert_form_edge_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = insert_form_edge_logic("Form1", "en")
        self.assertEqual(res, "Edge inserted into 'Form1'.")

    @patch('modules.forms.execute_fusion_script')
    def test_create_form_box_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["FormBox1"]}
        res = create_form_box_logic(10, 10, 10, 0, 0, 0, 2, 2, 2, "en")
        self.assertEqual(res, "Form box 'FormBox1' created.")

    @patch('modules.forms.execute_fusion_script')
    def test_create_form_box_unsupported(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["ERR_UNSUPPORTED"]}
        res = create_form_box_logic(10, 10, 10, 0, 0, 0, 2, 2, 2, "en")
        self.assertEqual(res, "Error: T-Spline primitive creation is not exposed by the current Fusion API/runtime.")

if __name__ == '__main__':
    unittest.main()
