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

    def test_register_tool_maps_localized_names(self):
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

        # Check if both DE and EN names were registered
        self.assertIn("skizze_erstellen", captured)
        self.assertIn("create_sketch", captured)

    def test_register_tool_uses_localized_signatures_for_sketch_polygon(self):
        mcp = MagicMock()
        captured = {}
        mcp.tool = lambda name, description: (lambda f: captured.update({name: f}) or f)

        def polygon_logic(sketch_name, cx, cy, radius, sides, lang="en"):
            return {
                "sketch_name": sketch_name,
                "center_x": cx,
                "center_y": cy,
                "radius": radius,
                "sides": sides
            }

        register_tool(mcp, "sketch_polygon", polygon_logic)

        de_sig = inspect.signature(captured["polygon_zeichnen"])
        en_sig = inspect.signature(captured["draw_polygon"])

        self.assertEqual(
            list(de_sig.parameters.keys()),
            ["skizzen_name", "center_x", "center_y", "radius", "seiten"],
        )
        self.assertEqual(
            list(en_sig.parameters.keys()),
            ["sketch_name", "center_x", "center_y", "radius", "sides"],
        )

    def test_register_tool_maps_localized_kwargs_for_sketch_polygon(self):
        mcp = MagicMock()
        captured = {}
        mcp.tool = lambda name, description: (lambda f: captured.update({name: f}) or f)

        def polygon_logic(sketch_name, cx, cy, radius, sides, lang="en"):
            return {
                "sketch_name": sketch_name,
                "center_x": cx,
                "center_y": cy,
                "radius": radius,
                "sides": sides
            }

        register_tool(mcp, "sketch_polygon", polygon_logic)

        de_result = captured["polygon_zeichnen"](
            skizzen_name="S1",
            center_x=1,
            center_y=2,
            radius=3,
            seiten=6
        )
        en_result = captured["draw_polygon"](
            sketch_name="S2",
            center_x=10,
            center_y=20,
            radius=30,
            sides=5
        )

        self.assertEqual(de_result["sketch_name"], "S1")
        self.assertEqual(de_result["sides"], 6)
        self.assertEqual(en_result["sketch_name"], "S2")
        self.assertEqual(en_result["sides"], 5)

    def test_register_tool_uses_localized_signatures_for_sketch_arc_and_circle(self):
        mcp = MagicMock()
        captured = {}
        mcp.tool = lambda name, description: (lambda f: captured.update({name: f}) or f)

        def arc_logic(sketch_name, cx, cy, sx, sy, angle, lang="en"):
            return {}
        def circle_logic(sketch_name, x, y, radius, lang="en"):
            return {}

        register_tool(mcp, "sketch_arc", arc_logic)
        register_tool(mcp, "draw_circle", circle_logic)

        de_arc_sig = inspect.signature(captured["bogen_zeichnen"])
        en_arc_sig = inspect.signature(captured["draw_arc"])
        de_circ_sig = inspect.signature(captured["kreis_zeichnen"])
        en_circ_sig = inspect.signature(captured["draw_circle"])

        self.assertEqual(
            list(de_arc_sig.parameters.keys()),
            ["skizzen_name", "mittelpunkt_x", "mittelpunkt_y", "start_x", "start_y", "winkel"],
        )
        self.assertEqual(
            list(en_arc_sig.parameters.keys()),
            ["sketch_name", "center_x", "center_y", "start_x", "start_y", "angle"],
        )
        self.assertEqual(
            list(de_circ_sig.parameters.keys()),
            ["skizzen_name", "center_x", "center_y", "radius"],
        )
        self.assertEqual(
            list(en_circ_sig.parameters.keys()),
            ["sketch_name", "center_x", "center_y", "radius"],
        )

    def test_register_tool_maps_localized_kwargs_for_sketch_create_arc_and_circle(self):
        mcp = MagicMock()
        captured = {}
        mcp.tool = lambda name, description: (lambda f: captured.update({name: f}) or f)

        def sketch_logic(plane_name="XY", name="Sketch1", lang="en"):
            return f"Mock {name} on {plane_name}"

        def arc_logic(sketch_name, cx, cy, sx, sy, angle, lang="en"):
            return {
                "sketch_name": sketch_name,
                "cx": cx,
                "cy": cy,
                "sx": sx,
                "sy": sy,
                "angle": angle
            }

        def circle_logic(sketch_name, x, y, radius, lang="en"):
            return {
                "sketch_name": sketch_name,
                "center_x": x,
                "center_y": y,
                "radius": radius
            }

        register_tool(mcp, "create_sketch", sketch_logic)
        register_tool(mcp, "sketch_arc", arc_logic)
        register_tool(mcp, "draw_circle", circle_logic)

        de_sketch_result = captured["skizze_erstellen"](name="S1", ebene="XZ")
        en_sketch_result = captured["create_sketch"](name="S2", plane="YZ")
        
        de_arc_result = captured["bogen_zeichnen"](
            skizzen_name="A1",
            mittelpunkt_x=1,
            mittelpunkt_y=2,
            start_x=3,
            start_y=4,
            winkel=45
        )
        en_arc_result = captured["draw_arc"](
            sketch_name="A2",
            center_x=10,
            center_y=20,
            start_x=30,
            start_y=40,
            angle=90
        )

        de_circ_result = captured["kreis_zeichnen"](
            skizzen_name="C1",
            center_x=5,
            center_y=6,
            radius=7
        )
        en_circ_result = captured["draw_circle"](
            sketch_name="C2",
            center_x=50,
            center_y=60,
            radius=70
        )

        self.assertIn("S1", de_sketch_result)
        self.assertIn("XZ", de_sketch_result)
        self.assertIn("S2", en_sketch_result)
        self.assertIn("YZ", en_sketch_result)

        self.assertEqual(de_arc_result["sketch_name"], "A1")
        self.assertEqual(de_arc_result["cx"], 1)
        self.assertEqual(de_arc_result["angle"], 45)
        self.assertEqual(en_arc_result["sketch_name"], "A2")
        self.assertEqual(en_arc_result["cx"], 10)
        self.assertEqual(en_arc_result["angle"], 90)

        self.assertEqual(de_circ_result["sketch_name"], "C1")
        self.assertEqual(de_circ_result["center_x"], 5)
        self.assertEqual(en_circ_result["sketch_name"], "C2")
        self.assertEqual(en_circ_result["center_x"], 50)

    def test_register_tool_signatures_for_sketch_modifiers(self):
        mcp = MagicMock()
        captured = {}
        mcp.tool = lambda name, description: (lambda f: captured.update({name: f}) or f)

        def circular_logic(sketch_name, center_x, center_y, count, lang="en"):
            return {}
        def rectangular_logic(sketch_name, count_x, dist_x, count_y=1, dist_y=0, lang="en"):
            return {}
        def offset_logic(sketch_name, distance, lang="en"):
            return {}

        register_tool(mcp, "sketch_circular_pattern", circular_logic)
        register_tool(mcp, "sketch_rectangular_pattern", rectangular_logic)
        register_tool(mcp, "sketch_offset", offset_logic)

        de_circular_sig = inspect.signature(captured["skizze_kreismuster"])
        en_circular_sig = inspect.signature(captured["sketch_circular_pattern"])
        de_rect_sig = inspect.signature(captured["skizze_rechteckmuster"])
        en_rect_sig = inspect.signature(captured["sketch_rectangular_pattern"])
        de_offset_sig = inspect.signature(captured["skizze_versatz"])
        en_offset_sig = inspect.signature(captured["sketch_offset"])

        self.assertEqual(
            list(de_circular_sig.parameters.keys()),
            ["skizzen_name", "center_x", "center_y", "anzahl"],
        )
        self.assertEqual(
            list(en_circular_sig.parameters.keys()),
            ["sketch_name", "center_x", "center_y", "count"],
        )
        self.assertEqual(
            list(de_rect_sig.parameters.keys()),
            ["skizzen_name", "anzahl_x", "distanz_x", "anzahl_y", "distanz_y"],
        )
        self.assertEqual(
            list(en_rect_sig.parameters.keys()),
            ["sketch_name", "count_x", "dist_x", "count_y", "dist_y"],
        )
        self.assertEqual(
            list(de_offset_sig.parameters.keys()),
            ["skizzen_name", "abstand"],
        )
        self.assertEqual(
            list(en_offset_sig.parameters.keys()),
            ["sketch_name", "distance"],
        )

    def test_register_tool_maps_localized_kwargs_for_sketch_modifiers(self):
        mcp = MagicMock()
        captured = {}
        mcp.tool = lambda name, description: (lambda f: captured.update({name: f}) or f)

        def circular_logic(sketch_name, center_x, center_y, count, lang="en"):
            return {
                "sketch_name": sketch_name,
                "cx": center_x,
                "cy": center_y,
                "count": count
            }
        def rectangular_logic(sketch_name, count_x, dist_x, count_y=1, dist_y=0, lang="en"):
            return {
                "sketch_name": sketch_name,
                "cx": count_x,
                "dx": dist_x,
                "cy": count_y,
                "dy": dist_y
            }
        def offset_logic(sketch_name, distance, lang="en"):
            return {
                "sketch_name": sketch_name,
                "dist": distance
            }

        register_tool(mcp, "sketch_circular_pattern", circular_logic)
        register_tool(mcp, "sketch_rectangular_pattern", rectangular_logic)
        register_tool(mcp, "sketch_offset", offset_logic)

        de_circular_result = captured["skizze_kreismuster"](
            skizzen_name="P1",
            center_x=1,
            center_y=2,
            anzahl=6
        )
        en_circular_result = captured["sketch_circular_pattern"](
            sketch_name="P2",
            center_x=10,
            center_y=20,
            count=4
        )
        de_rect_result = captured["skizze_rechteckmuster"](
            skizzen_name="R1",
            anzahl_x=3,
            distanz_x=5,
            anzahl_y=2,
            distanz_y=4
        )
        en_rect_result = captured["sketch_rectangular_pattern"](
            sketch_name="R2",
            count_x=30,
            dist_x=50,
            count_y=20,
            dist_y=40
        )
        de_offset_result = captured["skizze_versatz"](
            skizzen_name="O1",
            abstand=1.5
        )
        en_offset_result = captured["sketch_offset"](
            sketch_name="O2",
            distance=2.5
        )

        self.assertEqual(de_circular_result["sketch_name"], "P1")
        self.assertEqual(de_circular_result["count"], 6)
        self.assertEqual(en_circular_result["sketch_name"], "P2")
        self.assertEqual(en_circular_result["count"], 4)

        self.assertEqual(de_rect_result["sketch_name"], "R1")
        self.assertEqual(de_rect_result["cx"], 3)
        self.assertEqual(de_rect_result["dy"], 4)
        self.assertEqual(en_rect_result["sketch_name"], "R2")
        self.assertEqual(en_rect_result["cx"], 30)
        self.assertEqual(en_rect_result["dy"], 40)

        self.assertEqual(de_offset_result["sketch_name"], "O1")
        self.assertEqual(de_offset_result["dist"], 1.5)
        self.assertEqual(en_offset_result["sketch_name"], "O2")
        self.assertEqual(en_offset_result["dist"], 2.5)

    def test_draw_slot_uses_sketch_api_not_sketch_curves_collection(self):
        from unittest.mock import patch

        with patch('modules.sketch.execute_fusion_script') as mock_exec:
            mock_exec.return_value = {"data": ["OK"]}
            res = draw_slot_logic("S1", 30, 0, 40, 0, 2, "en")

        self.assertEqual(res, "Slot drawn.")
        script = mock_exec.call_args[0][0]
        self.assertIn("s.sketchCurves.sketchSlots.addCenterToCenterSlot(", script)
        self.assertIn("sw = float(params['w']) / 10.0", script)

    def test_sketch_circular_pattern_collects_typed_curve_collections(self):
        from unittest.mock import patch

        with patch('modules.sketch.execute_fusion_script') as mock_exec:
            mock_exec.return_value = {"data": ["OK"]}
            res = create_sketch_circular_pattern_logic("S1", 0, 0, 6, "en")

        self.assertEqual(res, "Sketch pattern created.")
        script = mock_exec.call_args[0][0]
        self.assertIn("constraints = s.geometricConstraints", script)
        self.assertIn("constraints.createCircularPatternInput(entities, center_point)", script)
        self.assertIn("constraints.addCircularPattern(pattern_input)", script)
        self.assertIn("s.sketchCurves.sketchLines", script)

    def test_sketch_rectangular_pattern_uses_constraint_api(self):
        from unittest.mock import patch

        with patch('modules.sketch.execute_fusion_script') as mock_exec:
            mock_exec.return_value = {"data": ["OK"]}
            res = create_sketch_rectangular_pattern_logic("S1", 3, 5, 2, 5, "en")

        self.assertEqual(res, "Sketch pattern created.")
        script = mock_exec.call_args[0][0]
        self.assertIn("constraints = s.geometricConstraints", script)
        self.assertIn("constraints.createRectangularPatternInput(entities,", script)
        self.assertIn("constraints.addRectangularPattern(pattern_input)", script)
        self.assertIn("dir1 = lines.addByTwoPoints(", script)
        self.assertIn("dir1.isConstruction = True", script)

    def test_sketch_offset_uses_point3d_not_sketch_point(self):
        from unittest.mock import patch

        with patch('modules.sketch.execute_fusion_script') as mock_exec:
            mock_exec.return_value = {"data": ["OK"]}
            res = create_sketch_offset_logic("S1", 1, "en")

        self.assertEqual(res, "Sketch offset created.")
        script = mock_exec.call_args[0][0]
        self.assertIn("offset_point = adsk.core.Point3D.create(10.0, 10.0, 0)", script)
        self.assertIn("s.offset(entities, offset_point, params['dist'])", script)

if __name__ == '__main__':
    unittest.main()
