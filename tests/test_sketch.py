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
        self.assertIn("draw_center_rectangle", script)
        self.assertIn("draw_three_point_rectangle", script)
        self.assertIn("draw_overall_slot", script)
        self.assertIn("draw_center_point_slot", script)
        self.assertIn("draw_text", script)
        self.assertIn("draw_inscribed_polygon", script)
        self.assertIn("draw_circumscribed_polygon", script)
        self.assertIn("draw_edge_polygon", script)
        self.assertIn("project_cut_edges", script)
        self.assertIn("include_geometry", script)
        self.assertIn("project_to_surface", script)
        self.assertIn("redefine", script)
        self.assertIn("find_connected_curves", script)
        self.assertIn("def add_overall_slot(start_point, end_point, width_value):", script)
        self.assertIn("def add_center_point_slot(center_point, direction_point, width_value):", script)
        self.assertIn("def add_center_rectangle(center_point, corner_point):", script)
        self.assertIn("def add_three_point_rectangle(point_one, point_two, point_three):", script)
        self.assertIn("def add_edge_polygon(point_one, point_two, sides, flip=False):", script)
        self.assertIn("def collect_projection_entities(op):", script)
        self.assertIn("def project_entities_to_sketch(entities, is_linked=False):", script)
        self.assertIn("def resolve_spun_profile_entities(op):", script)
        self.assertIn("def resolve_spun_profile_axis(op, default_owner):", script)
        self.assertIn("s.projectCutEdges(body)", script)
        self.assertIn("s.include(entity)", script)
        self.assertIn("s.projectToSurface(faces, source_curves, project_type", script)
        self.assertIn("s.findConnectedCurves(seed_curve)", script)
        self.assertIn("s.referencePlane = target_plane", script)

    @patch('core.bridge.requests.post')
    def test_edit_sketch_batch_sends_new_sketch_create_actions(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["draw_text:OK"]}
        mock_post.return_value = mock_response

        ops = [
            {"action": "draw_center_rectangle", "cx": 10, "cy": 10, "x": 14, "y": 12},
            {"action": "draw_three_point_rectangle", "x1": 0, "y1": 0, "x2": 6, "y2": 0, "x3": 0, "y3": 3},
            {"action": "draw_overall_slot", "x1": 20, "y1": 5, "x2": 30, "y2": 5, "width": 2},
            {"action": "draw_center_point_slot", "cx": 40, "cy": 10, "x": 45, "y": 10, "width": 2},
            {"action": "draw_text", "text": "LABEL", "x": 5, "y": 20, "height": 1.5, "font": "Arial"},
            {"action": "draw_inscribed_polygon", "cx": 50, "cy": 50, "r": 4, "sides": 6},
            {"action": "draw_circumscribed_polygon", "cx": 60, "cy": 60, "r": 4, "sides": 5},
            {"action": "draw_edge_polygon", "x1": 70, "y1": 70, "x2": 74, "y2": 70, "sides": 6, "flip": True},
        ]
        res = edit_sketch_logic("MySketch", ops, "en")

        self.assertEqual(res, "Sketch 'MySketch' updated successfully.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['operations'][0]['action'], "draw_center_rectangle")
        self.assertEqual(params['operations'][3]['action'], "draw_center_point_slot")
        self.assertEqual(params['operations'][4]['text'], "LABEL")
        self.assertEqual(params['operations'][7]['flip'], True)

    @patch('core.bridge.requests.post')
    def test_edit_sketch_batch_sends_projection_and_redefine_actions(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["project_geometry:OK"]}
        mock_post.return_value = mock_response

        ops = [
            {"action": "project_geometry", "body": "BodyA", "face_index": 0, "is_linked": True},
            {"action": "project_cut_edges", "body": "BodyA"},
            {"action": "include_geometry", "body": "BodyA", "edge_indices": [0, 1]},
            {"action": "project_to_surface", "body": "BodyA", "face_indices": [0, 1], "curve_indices": [0, 1], "projection_type": "along_vector", "direction_axis": "z"},
            {"action": "redefine", "plane_name": "XZ"},
            {"action": "find_connected_curves", "curve_index": 0},
            {"action": "offset", "dist": 1.0, "seed_curve_index": 0},
        ]
        res = edit_sketch_logic("MySketch", ops, "en")

        self.assertEqual(res, "Sketch 'MySketch' updated successfully.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['operations'][0]['is_linked'], True)
        self.assertEqual(params['operations'][2]['edge_indices'], [0, 1])
        self.assertEqual(params['operations'][3]['projection_type'], "along_vector")
        self.assertEqual(params['operations'][4]['plane_name'], "XZ")
        self.assertEqual(params['operations'][6]['seed_curve_index'], 0)

    @patch('core.bridge.requests.post')
    def test_edit_sketch_batch_sends_extended_spun_profile_inputs(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["create_spun_profile:OK"]}
        mock_post.return_value = mock_response

        ops = [
            {
                "action": "create_spun_profile",
                "body": "TurningBlank",
                "face_indices": [0, 1],
                "axis_curve_index": 2,
                "is_centerline_added": True,
                "tolerance": 0.005,
            },
            {
                "action": "create_spun_profile",
                "bodies": ["BlankA", "BlankB"],
                "axis_body": "AxisCarrier",
                "axis_edge_index": 0,
                "flip_result": True,
            },
        ]
        res = edit_sketch_logic("MySketch", ops, "en")

        self.assertEqual(res, "Sketch 'MySketch' updated successfully.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['operations'][0]['face_indices'], [0, 1])
        self.assertEqual(params['operations'][0]['axis_curve_index'], 2)
        self.assertEqual(params['operations'][1]['bodies'], ["BlankA", "BlankB"])
        self.assertEqual(params['operations'][1]['axis_edge_index'], 0)

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
