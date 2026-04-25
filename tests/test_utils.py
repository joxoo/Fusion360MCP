import unittest
import inspect
from core.utils import format_response, register_tool, load_i18n
from unittest.mock import MagicMock

class TestUtils(unittest.TestCase):
    def test_format_response_en(self):
        # Using a key that exists in i18n.json (box_created)
        res = format_response("en", "box_created", name="World")
        self.assertEqual(res, "Box 'World' created.")

    def test_format_response_de(self):
        # Using a key that exists in i18n.json (box_created)
        res = format_response("de", "box_created", name="Welt")
        self.assertEqual(res, "Box 'Welt' erstellt.")

    def test_format_response_fallback(self):
        # Using a non-existent key should return the key itself
        res = format_response("en", "non_existent_key")
        self.assertEqual(res, "non_existent_key")

    def test_register_tool(self):
        mcp = MagicMock()
        def mock_func(lang, param1):
            return f"{lang}_{param1}"
        
        # Test registering 'create_box' which exists in i18n.json
        register_tool(mcp, "create_box", mock_func)
        
        # Check if mcp.tool was called for both de and en
        # i18n.json has 'box_erstellen' for de and 'create_box' for en
        tool_names = [call.kwargs.get('name') for call in mcp.tool.call_args_list]
        self.assertIn("box_erstellen", tool_names)
        self.assertIn("create_box", tool_names)

    def test_register_tool_uses_localized_signatures(self):
        captured = {}

        def tool_decorator(**tool_kwargs):
            def decorator(func):
                captured[tool_kwargs["name"]] = func
                return func
            return decorator

        mcp = MagicMock()
        mcp.tool.side_effect = tool_decorator

        def polygon_logic(sketch_name, cx, cy, radius, sides, lang="en"):
            return {
                "lang": lang,
                "sketch_name": sketch_name,
                "cx": cx,
                "cy": cy,
                "radius": radius,
                "sides": sides,
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

    def test_register_tool_maps_localized_kwargs_to_canonical_args(self):
        captured = {}

        def tool_decorator(**tool_kwargs):
            def decorator(func):
                captured[tool_kwargs["name"]] = func
                return func
            return decorator

        mcp = MagicMock()
        mcp.tool.side_effect = tool_decorator

        def polygon_logic(sketch_name, cx, cy, radius, sides, lang="en"):
            return {
                "lang": lang,
                "sketch_name": sketch_name,
                "cx": cx,
                "cy": cy,
                "radius": radius,
                "sides": sides,
            }

        register_tool(mcp, "sketch_polygon", polygon_logic)

        de_result = captured["polygon_zeichnen"](
            skizzen_name="S1",
            center_x=10,
            center_y=20,
            radius=3,
            seiten=6,
        )
        en_result = captured["draw_polygon"](
            sketch_name="S2",
            center_x=1,
            center_y=2,
            radius=4,
            sides=8,
        )

        self.assertEqual(
            de_result,
            {
                "lang": "de",
                "sketch_name": "S1",
                "cx": 10,
                "cy": 20,
                "radius": 3,
                "sides": 6,
            },
        )
        self.assertEqual(
            en_result,
            {
                "lang": "en",
                "sketch_name": "S2",
                "cx": 1,
                "cy": 2,
                "radius": 4,
                "sides": 8,
            },
        )

    def test_register_tool_uses_localized_signatures_for_sketch_arc_and_circle(self):
        captured = {}

        def tool_decorator(**tool_kwargs):
            def decorator(func):
                captured[tool_kwargs["name"]] = func
                return func
            return decorator

        mcp = MagicMock()
        mcp.tool.side_effect = tool_decorator

        def arc_logic(sketch_name, cx, cy, sx, sy, angle, lang="en"):
            return None

        def circle_logic(sketch_name, x, y, radius, lang="en"):
            return None

        register_tool(mcp, "sketch_arc", arc_logic)
        register_tool(mcp, "draw_circle", circle_logic)

        de_arc_sig = inspect.signature(captured["bogen_zeichnen"])
        en_arc_sig = inspect.signature(captured["draw_arc"])
        de_circle_sig = inspect.signature(captured["kreis_zeichnen"])
        en_circle_sig = inspect.signature(captured["draw_circle"])

        self.assertEqual(
            list(de_arc_sig.parameters.keys()),
            ["skizzen_name", "mittelpunkt_x", "mittelpunkt_y", "start_x", "start_y", "winkel"],
        )
        self.assertEqual(
            list(en_arc_sig.parameters.keys()),
            ["sketch_name", "center_x", "center_y", "start_x", "start_y", "angle"],
        )
        self.assertEqual(
            list(de_circle_sig.parameters.keys()),
            ["skizzen_name", "center_x", "center_y", "radius"],
        )
        self.assertEqual(
            list(en_circle_sig.parameters.keys()),
            ["sketch_name", "center_x", "center_y", "radius"],
        )

    def test_register_tool_maps_localized_kwargs_for_sketch_create_arc_and_circle(self):
        captured = {}

        def tool_decorator(**tool_kwargs):
            def decorator(func):
                captured[tool_kwargs["name"]] = func
                return func
            return decorator

        mcp = MagicMock()
        mcp.tool.side_effect = tool_decorator

        def sketch_logic(plane_name="XY", name="Sketch1", lang="en"):
            return {"lang": lang, "plane_name": plane_name, "name": name}

        def arc_logic(sketch_name, cx, cy, sx, sy, angle, lang="en"):
            return {
                "lang": lang,
                "sketch_name": sketch_name,
                "cx": cx,
                "cy": cy,
                "sx": sx,
                "sy": sy,
                "angle": angle,
            }

        def circle_logic(sketch_name, x, y, radius, lang="en"):
            return {
                "lang": lang,
                "sketch_name": sketch_name,
                "x": x,
                "y": y,
                "radius": radius,
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
            winkel=90,
        )
        en_arc_result = captured["draw_arc"](
            sketch_name="A2",
            center_x=5,
            center_y=6,
            start_x=7,
            start_y=8,
            angle=45,
        )
        de_circle_result = captured["kreis_zeichnen"](
            skizzen_name="C1",
            center_x=9,
            center_y=10,
            radius=11,
        )
        en_circle_result = captured["draw_circle"](
            sketch_name="C2",
            center_x=12,
            center_y=13,
            radius=14,
        )

        self.assertEqual(
            de_sketch_result,
            {"lang": "de", "plane_name": "XZ", "name": "S1"},
        )
        self.assertEqual(
            en_sketch_result,
            {"lang": "en", "plane_name": "YZ", "name": "S2"},
        )
        self.assertEqual(
            de_arc_result,
            {
                "lang": "de",
                "sketch_name": "A1",
                "cx": 1,
                "cy": 2,
                "sx": 3,
                "sy": 4,
                "angle": 90,
            },
        )
        self.assertEqual(
            en_arc_result,
            {
                "lang": "en",
                "sketch_name": "A2",
                "cx": 5,
                "cy": 6,
                "sx": 7,
                "sy": 8,
                "angle": 45,
            },
        )
        self.assertEqual(
            de_circle_result,
            {
                "lang": "de",
                "sketch_name": "C1",
                "x": 9,
                "y": 10,
                "radius": 11,
            },
        )
        self.assertEqual(
            en_circle_result,
            {
                "lang": "en",
                "sketch_name": "C2",
                "x": 12,
                "y": 13,
                "radius": 14,
            },
        )

    def test_register_tool_uses_localized_signatures_for_patterns_and_offset(self):
        captured = {}

        def tool_decorator(**tool_kwargs):
            def decorator(func):
                captured[tool_kwargs["name"]] = func
                return func
            return decorator

        mcp = MagicMock()
        mcp.tool.side_effect = tool_decorator

        def circular_logic(sketch_name, center_x, center_y, count, lang="en"):
            return None

        def rectangular_logic(sketch_name, count_x, dist_x, count_y=1, dist_y=0, lang="en"):
            return None

        def offset_logic(sketch_name, distance, lang="en"):
            return None

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

    def test_register_tool_maps_localized_kwargs_for_patterns_and_offset(self):
        captured = {}

        def tool_decorator(**tool_kwargs):
            def decorator(func):
                captured[tool_kwargs["name"]] = func
                return func
            return decorator

        mcp = MagicMock()
        mcp.tool.side_effect = tool_decorator

        def circular_logic(sketch_name, center_x, center_y, count, lang="en"):
            return {
                "lang": lang,
                "sketch_name": sketch_name,
                "center_x": center_x,
                "center_y": center_y,
                "count": count,
            }

        def rectangular_logic(sketch_name, count_x, dist_x, count_y=1, dist_y=0, lang="en"):
            return {
                "lang": lang,
                "sketch_name": sketch_name,
                "count_x": count_x,
                "dist_x": dist_x,
                "count_y": count_y,
                "dist_y": dist_y,
            }

        def offset_logic(sketch_name, distance, lang="en"):
            return {
                "lang": lang,
                "sketch_name": sketch_name,
                "distance": distance,
            }

        register_tool(mcp, "sketch_circular_pattern", circular_logic)
        register_tool(mcp, "sketch_rectangular_pattern", rectangular_logic)
        register_tool(mcp, "sketch_offset", offset_logic)

        de_circular_result = captured["skizze_kreismuster"](
            skizzen_name="P1",
            center_x=1,
            center_y=2,
            anzahl=6,
        )
        en_circular_result = captured["sketch_circular_pattern"](
            sketch_name="P2",
            center_x=3,
            center_y=4,
            count=8,
        )
        de_rect_result = captured["skizze_rechteckmuster"](
            skizzen_name="R1",
            anzahl_x=2,
            distanz_x=5,
            anzahl_y=3,
            distanz_y=6,
        )
        en_rect_result = captured["sketch_rectangular_pattern"](
            sketch_name="R2",
            count_x=4,
            dist_x=7,
            count_y=5,
            dist_y=8,
        )
        de_offset_result = captured["skizze_versatz"](
            skizzen_name="O1",
            abstand=1.5,
        )
        en_offset_result = captured["sketch_offset"](
            sketch_name="O2",
            distance=2.5,
        )

        self.assertEqual(
            de_circular_result,
            {
                "lang": "de",
                "sketch_name": "P1",
                "center_x": 1,
                "center_y": 2,
                "count": 6,
            },
        )
        self.assertEqual(
            en_circular_result,
            {
                "lang": "en",
                "sketch_name": "P2",
                "center_x": 3,
                "center_y": 4,
                "count": 8,
            },
        )
        self.assertEqual(
            de_rect_result,
            {
                "lang": "de",
                "sketch_name": "R1",
                "count_x": 2,
                "dist_x": 5,
                "count_y": 3,
                "dist_y": 6,
            },
        )
        self.assertEqual(
            en_rect_result,
            {
                "lang": "en",
                "sketch_name": "R2",
                "count_x": 4,
                "dist_x": 7,
                "count_y": 5,
                "dist_y": 8,
            },
        )
        self.assertEqual(
            de_offset_result,
            {
                "lang": "de",
                "sketch_name": "O1",
                "distance": 1.5,
            },
        )
        self.assertEqual(
            en_offset_result,
            {
                "lang": "en",
                "sketch_name": "O2",
                "distance": 2.5,
            },
        )

if __name__ == '__main__':
    unittest.main()
