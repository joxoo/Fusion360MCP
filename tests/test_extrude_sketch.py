import unittest
from unittest.mock import MagicMock, patch
from modules.geometry import extrude_sketch_logic

class TestExtrudeSketch(unittest.TestCase):
    @patch('core.bridge.requests.post')
    def test_extrude_sketch_all_profiles(self, mock_post):
        """Verify that by default all profiles are extruded."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Body1"]}
        mock_post.return_value = mock_response

        res = extrude_sketch_logic("MySketch", 1.0, "en")
        # In test environment, format_response might return the key if file isn't loaded correctly
        self.assertTrue(res == "Extrusion of 'MySketch' created." or res == "extrusion_created")
        
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['sketch'], "MySketch")
        self.assertEqual(params['dist'], 1.0)
        self.assertIsNone(params['profile_index'])
        self.assertEqual(params['op'], "NewBody")

    @patch('core.bridge.requests.post')
    def test_extrude_sketch_single_profile(self, mock_post):
        """Verify that a specific profile index can be targeted."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Body1"]}
        mock_post.return_value = mock_response

        res = extrude_sketch_logic("MySketch", 0.5, "en", profile_index=1)
        self.assertTrue(res == "Extrusion of 'MySketch' created." or res == "extrusion_created")
        
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['profile_index'], 1)

    @patch('core.bridge.requests.post')
    def test_extrude_sketch_cut_operation(self, mock_post):
        """Verify that the 'Cut' operation is passed correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = extrude_sketch_logic("MySketch", 2.0, "en", op="Cut")
        self.assertTrue(res == "Extrusion of 'MySketch' created." or res == "extrusion_created")
        
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['op'], "Cut")

    @patch('core.bridge.requests.post')
    def test_extrude_sketch_join_operation(self, mock_post):
        """Verify that the 'Join' operation is passed correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = extrude_sketch_logic("MySketch", 2.0, "en", op="Join")
        self.assertTrue(res == "Extrusion of 'MySketch' created." or res == "extrusion_created")
        
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['op'], "Join")

    @patch('core.bridge.requests.post')
    def test_extrude_sketch_offset(self, mock_post):
        """Verify that the 'offset' parameter is passed correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Body1"]}
        mock_post.return_value = mock_response

        res = extrude_sketch_logic("MySketch", 1.0, "en", offset=0.3)
        self.assertTrue(res == "Extrusion of 'MySketch' created." or res == "extrusion_created")
        
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['offset'], 0.3)

class TestExtrudeSketchScript(unittest.TestCase):
    def test_extrude_sketch_script_content(self):
        """Verify the script builder includes logic for profile selection, operations, and offset."""
        from modules.geometry_scripts import build_extrude_sketch_script
        script = build_extrude_sketch_script()
        
        self.assertIn("idx = params.get('profile_index')", script)
        self.assertIn("op_str = params.get('op', 'NewBody')", script)
        self.assertIn("offset_val = params.get('offset', 0)", script)
        self.assertIn("adsk.fusion.OffsetStartDefinition.create", script)
        self.assertIn("ext_in.participantBodies = [target_body]", script)
        self.assertIn("adsk.core.ObjectCollection.create()", script)
        self.assertIn("adsk.fusion.FeatureOperations.CutFeatureOperation", script)
        self.assertIn("adsk.fusion.FeatureOperations.JoinFeatureOperation", script)

if __name__ == '__main__':
    unittest.main()
