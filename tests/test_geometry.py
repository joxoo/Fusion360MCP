import unittest
from unittest.mock import MagicMock, patch
from core.bridge import execute_fusion_script
from modules.geometry import create_box_logic, create_hole_logic

class TestGeometry(unittest.TestCase):
    @patch('core.bridge.requests.post')
    def test_create_box_params(self, mock_post):
        # Configure mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["MyBox"]}
        mock_post.return_value = mock_response

        # Execute logic (Signature: l, w, h, name, x, y, z, op, taper, lang)
        res = create_box_logic(10, 20, 5, "MyBox", 1, 2, 3, "NewBody", 0, "en")
        
        # Verify
        self.assertEqual(res, "Box 'MyBox' created.")
        sent_payload = mock_post.call_args[1]['json']
        params = sent_payload['payload']['params']
        self.assertEqual(params['l'], 10)
        self.assertEqual(params['x'], 1)

    @patch('core.bridge.requests.post')
    def test_create_box_with_z_offset_uses_offset_plane(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OffsetBox"]}
        mock_post.return_value = mock_response

        res = create_box_logic(5, 10, 0.2, "OffsetBox", 5, 0, 1.5, "NewBody", 0, "en")

        self.assertEqual(res, "Box 'OffsetBox' created.")
        script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("translate_body(body, params['x'], params['y'], params['z'])", script)
        self.assertIn("move_input.defineAsTranslateXYZ(", script)

    @patch('core.bridge.requests.post')
    def test_create_hole_sets_extent(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = create_hole_logic(10, 0, 0, "en")

        self.assertEqual(res, "Hole created.")
        script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(1000.0))", script)
        self.assertIn("plane = get_offset_plane(root.xYConstructionPlane, params['z'])", script)
        self.assertIn("sketch.sketchCurves.sketchCircles.addByCenterRadius(center, params['d'] / 20.0)", script)
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['d'], 10)
        self.assertEqual(params['z'], 0)

if __name__ == '__main__':
    unittest.main()
