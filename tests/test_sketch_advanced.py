import unittest
from unittest.mock import MagicMock, patch
from modules.sketch import (
    sketch_project_logic,
    draw_sketch_text_logic,
    draw_ellipse_logic
)

class TestSketchAdvanced(unittest.TestCase):
    @patch('modules.sketch.execute_fusion_script')
    def test_sketch_project_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = sketch_project_logic("S1", "Body1", "en")
        self.assertEqual(res, "Sketch projected.")
        args = mock_exec.call_args[0]
        self.assertEqual(args[1]['sketch'], "S1")
        self.assertEqual(args[1]['body'], "Body1")

    @patch('modules.sketch.execute_fusion_script')
    def test_draw_sketch_text_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = draw_sketch_text_logic("S1", "Hello", 0, 0, 1.0, "Arial", "en")
        self.assertEqual(res, "Text added.")
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['text'], "Hello")
        self.assertEqual(params['font'], "Arial")

    @patch('modules.sketch.execute_fusion_script')
    def test_draw_ellipse_params(self, mock_exec):
        mock_exec.return_value = {"status": "success", "data": ["OK"]}
        res = draw_ellipse_logic("S1", 0, 0, 5, 0, 0, 3, "en")
        self.assertEqual(res, "Ellipse drawn.")
        params = mock_exec.call_args[0][1]
        self.assertEqual(params['cx'], 0)
        self.assertEqual(params['mx'], 5)

if __name__ == '__main__':
    unittest.main()
