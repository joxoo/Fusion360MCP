import unittest
from unittest.mock import MagicMock, patch
from core.utils import format_response, register_tool, load_i18n
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

        # Check if only canonical name was registered
        self.assertIn("create_sketch", captured)
        self.assertNotIn("skizze_erstellen", captured)

    def test_register_tool_signature_excludes_lang(self):
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

    def test_register_tool_wrapper_handles_extra_kwargs(self):
        mcp = MagicMock()
        captured = {}
        mcp.tool = lambda name, description: (lambda f: captured.update({name: f}) or f)

        def dummy_logic(name, lang="en"):
            return f"Result for {name} ({lang})"

        register_tool(mcp, "dummy_tool", dummy_logic)
        
        # Call with extra kwargs that Gemini might send
        res = captured["dummy_tool"](name="Test", wait_for_previous=True)
        self.assertEqual(res, "Result for Test (en)")

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

if __name__ == '__main__':
    unittest.main()
