import unittest
from unittest.mock import MagicMock, patch
from modules.sketch import (
    create_sketch_logic,
    edit_sketch_logic,
    create_sketch_circular_pattern_logic
)

from core.utils import load_i18n

class TestSketch(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_create_sketch_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["MySketch"]}
        mock_post.return_value = mock_response

        res = create_sketch_logic("XZ", "MySketch", "en")
        
        self.assertEqual(res, "Sketch 'MySketch' created.")
        sent_payload = mock_post.call_args[1]['json']
        params = sent_payload['payload']['params']
        self.assertEqual(params['plane'], "XZ")
        self.assertEqual(params['name'], "MySketch")

    @patch('core.bridge.requests.post')
    def test_edit_sketch_batch(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["draw_line:OK"]}
        mock_post.return_value = mock_response

        ops = [{"action": "draw_line", "x1": 0, "y1": 0, "x2": 10, "y2": 10}]
        res = edit_sketch_logic("MySketch", ops, "en")
        
        self.assertEqual(res, "Sketch 'MySketch' updated successfully.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['sketch'], "MySketch")
        self.assertEqual(params['operations'][0]['action'], "draw_line")
        script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("for op in params.get('operations', []):", script)
        self.assertIn("delete_curve", script)
        self.assertIn("clear_sketch", script)
        self.assertIn("draw_arc", script)
        self.assertIn("curve_ref", script)
        self.assertIn("get_selected_curves", script)
        self.assertIn("move_entities", script)
        self.assertIn("copy_entities", script)
        self.assertIn("mirror_entities", script)
        self.assertIn("get_mirror_axis", script)
        self.assertIn("transform.setCell(0, 0, r00)", script)
        self.assertIn("s.copy(entities, transform)", script)
        self.assertIn("s.move(entities, transform)", script)
        self.assertIn("s.copy(entities, transform)", script)
        self.assertIn("remove_constraint", script)
        self.assertIn("set_dimension", script)
        self.assertIn("delete_dimension", script)

    @patch('core.bridge.requests.post')
    def test_edit_sketch_batch_reports_errors(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["delete_curve:ERR_CURVE_NOT_FOUND"]}
        mock_post.return_value = mock_response

        ops = [{"action": "delete_curve", "curve_index": 4}]
        res = edit_sketch_logic("MySketch", ops, "en")

        self.assertEqual(
            res,
            "Error updating sketch 'MySketch': delete_curve:ERR_CURVE_NOT_FOUND -> Error: Target sketch curve not found.",
        )

    @patch('core.bridge.requests.post')
    def test_edit_sketch_accepts_sketch_ref_and_curve_ref(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["delete_curve:OK"]}
        mock_post.return_value = mock_response

        res = edit_sketch_logic(
            operations=[{"action": "delete_curve", "curve_ref": {"curve_index": 2}}],
            sketch_ref={"sketch": "ScopedSketch", "component_path": "Root/SubAssembly"},
            lang="en",
        )

        self.assertEqual(res, "Sketch 'ScopedSketch' updated successfully.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['sketch'], "ScopedSketch")
        self.assertEqual(params['component_path'], "Root/SubAssembly")
        self.assertEqual(params['operations'][0]['curve_ref']['curve_index'], 2)

    @patch('core.bridge.requests.post')
    def test_edit_sketch_accepts_constraint_and_dimension_refs(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["remove_constraint:OK,set_dimension:OK"]}
        mock_post.return_value = mock_response

        res = edit_sketch_logic(
            operations=[
                {"action": "remove_constraint", "constraint_ref": {"constraint_index": 1}},
                {"action": "set_dimension", "dimension_ref": {"dimension_index": 0}, "value": 2.5},
            ],
            sketch_ref={"sketch": "ScopedSketch", "component_path": "Root/SubAssembly"},
            lang="en",
        )

        self.assertEqual(res, "Sketch 'ScopedSketch' updated successfully.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['operations'][0]['constraint_ref']['constraint_index'], 1)
        self.assertEqual(params['operations'][1]['dimension_ref']['dimension_index'], 0)

    @patch('core.bridge.requests.post')
    def test_edit_sketch_reports_mirror_axis_errors(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["mirror_entities:ERR_MIRROR_AXIS_REQUIRED"]}
        mock_post.return_value = mock_response

        res = edit_sketch_logic(
            operations=[{"action": "mirror_entities", "curve_indices": [1, 2]}],
            sketch_ref={"sketch": "ScopedSketch", "component_path": "Root/SubAssembly"},
            lang="en",
        )

        self.assertIn("mirror_curve_index or mirror_curve_ref is required", res)

if __name__ == '__main__':
    unittest.main()
