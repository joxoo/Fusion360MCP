import unittest
from unittest.mock import MagicMock, patch
from core.utils import COMMON_FUSION_SCRIPTS, format_response, register_tool, load_i18n
from core.error_handler import get_result_value, localized_error, map_result_error
import inspect
from modules.sketch import draw_slot_logic, create_sketch_circular_pattern_logic, create_sketch_rectangular_pattern_logic, create_sketch_offset_logic

class TestUtils(unittest.TestCase):
    def setUp(self):
        # Reset I18N data or ensure it's loaded
        load_i18n()

    def test_format_response_en(self):
        res = format_response("en", "sketch_created", name="S1")
        self.assertEqual(res, "Sketch 'S1' created.")

    def test_format_response_de(self):
        res = format_response("de", "sketch_created", name="S1")
        self.assertEqual(res, "Skizze 'S1' erstellt.")

    def test_register_tool_canonical_only(self):
        mcp = MagicMock()
        captured = {}

        # Mock the tool decorator
        def mock_tool(name, description):
            def decorator(f):
                captured[name] = f
                return f
            return decorator
        mcp.tool = mock_tool

        def dummy_logic(plane_name="XY", name="Sketch1", lang="en"):
            return f"Mock {name} on {plane_name}"

        register_tool(mcp, "create_sketch", dummy_logic)

        # Check canonical name plus supported compatibility alias
        self.assertIn("create_sketch", captured)
        self.assertIn("skizze_erstellen", captured)

    def test_register_tool_signature_hides_lang(self):
        mcp = MagicMock()
        captured = {}
        mcp.tool = lambda name, description: (lambda f: captured.update({name: f}) or f)

        def polygon_logic(sketch_name, cx, cy, radius, sides, lang="en"):
            return {}

        register_tool(mcp, "sketch_polygon", polygon_logic)

        en_sig = inspect.signature(captured["sketch_polygon"])
        self.assertEqual(
            list(en_sig.parameters.keys()),
            ["sketch_name", "cx", "cy", "radius", "sides"],
        )
        self.assertNotIn("lang", en_sig.parameters)

    def test_register_tool_filters_extra_kwargs_and_sets_default_lang(self):
        mcp = MagicMock()
        captured = {}
        mcp.tool = lambda name, description: (lambda f: captured.update({name: f}) or f)

        observed = {}

        def snap_logic(path_sketch, lang="en"):
            observed["path_sketch"] = path_sketch
            observed["lang"] = lang
            return "OK"

        register_tool(mcp, "create_snap_fit", snap_logic)
        result = captured["create_snap_fit"](path_sketch="SnapFit_Path", wait_for_previous=True)

        self.assertEqual(result, "OK")
        self.assertEqual(observed, {"path_sketch": "SnapFit_Path", "lang": "en"})

    def test_register_tool_maps_parameter_aliases(self):
        mcp = MagicMock()
        captured = {}
        mcp.tool = lambda name, description: (lambda f: captured.update({name: f}) or f)

        observed = {}

        def polygon_logic(sketch_name, cx, cy, radius, sides, lang="en"):
            observed.update({
                "sketch_name": sketch_name,
                "cx": cx,
                "cy": cy,
                "radius": radius,
                "sides": sides,
                "lang": lang,
            })
            return "OK"

        register_tool(mcp, "sketch_polygon", polygon_logic)
        result = captured["polygon_zeichnen"](
            skizzen_name="SmokeSketch",
            center_x=10,
            center_y=10,
            radius=3,
            seiten=6,
        )

        self.assertEqual(result, "OK")
        self.assertEqual(observed["sketch_name"], "SmokeSketch")
        self.assertEqual(observed["cx"], 10)
        self.assertEqual(observed["cy"], 10)
        self.assertEqual(observed["radius"], 3)
        self.assertEqual(observed["sides"], 6)
        self.assertEqual(observed["lang"], "en")

    def test_alias_tool_signature_exposes_alias_parameter_names(self):
        mcp = MagicMock()
        captured = {}
        mcp.tool = lambda name, description: (lambda f: captured.update({name: f}) or f)

        def polygon_logic(sketch_name, cx, cy, radius, sides, lang="en"):
            return "OK"

        register_tool(mcp, "sketch_polygon", polygon_logic)

        alias_sig = inspect.signature(captured["polygon_zeichnen"])
        self.assertEqual(
            list(alias_sig.parameters.keys()),
            ["skizzen_name", "center_x", "center_y", "radius", "seiten"],
        )

    def test_draw_slot_uses_sketch_api_not_sketch_curves_collection(self):
        with patch('modules.sketch.execute_fusion_script') as mock_exec:
            mock_exec.return_value = {"data": ["OK"]}
            res = draw_slot_logic("S1", 30, 0, 40, 0, 2, "en")

        self.assertEqual(res, "Slot drawn.")
        script = mock_exec.call_args[0][0]
        self.assertIn("s.sketchCurves.sketchSlots.addCenterToCenterSlot(", script)
        self.assertIn("sw = float(params['w']) / 10.0", script)

    def test_sketch_circular_pattern_collects_typed_curve_collections(self):
        with patch('modules.sketch.execute_fusion_script') as mock_exec:
            mock_exec.return_value = {"data": ["OK"]}
            res = create_sketch_circular_pattern_logic("S1", 0, 0, 6, "en")

        self.assertEqual(res, "Sketch pattern created.")
        script = mock_exec.call_args[0][0]
        self.assertIn("constraints = s.geometricConstraints", script)
        self.assertIn("constraints.createCircularPatternInput(entities, center_point)", script)
        self.assertIn("constraints.addCircularPattern(pattern_input)", script)

    def test_sketch_rectangular_pattern_uses_constraint_api(self):
        with patch('modules.sketch.execute_fusion_script') as mock_exec:
            mock_exec.return_value = {"data": ["OK"]}
            res = create_sketch_rectangular_pattern_logic("S1", 3, 5, 2, 5, "en")

        self.assertEqual(res, "Sketch pattern created.")
        script = mock_exec.call_args[0][0]
        self.assertIn("constraints = s.geometricConstraints", script)
        self.assertIn("constraints.createRectangularPatternInput(entities,", script)
        self.assertIn("constraints.addRectangularPattern(pattern_input)", script)

    def test_error_handler_reads_result_value(self):
        self.assertEqual(get_result_value({"data": ["OK"]}), "OK")
        self.assertEqual(get_result_value({}, "fallback"), "fallback")

    def test_error_handler_maps_localized_error(self):
        res = map_result_error("ERR_COMPONENT", "en", {
            "ERR_COMPONENT": localized_error("component_not_found")
        })
        self.assertEqual(res, "Component not found.")

    def test_error_handler_passthroughs_unknown_err_codes(self):
        res = map_result_error("ERR_SOMETHING", "en", {})
        self.assertEqual(res, "ERR_SOMETHING")

    def test_find_body_common_script_prefers_exact_component_path_segments(self):
        script = COMMON_FUSION_SCRIPTS["find_body"]
        self.assertIn("exact_segment = normalize_name(segment)", script)
        self.assertIn("if occ_name == exact_segment or comp_name == exact_segment:", script)
        self.assertIn("if match:", script)
        self.assertIn("continue", script)

if __name__ == '__main__':
    unittest.main()
