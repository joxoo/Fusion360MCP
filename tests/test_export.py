import unittest
from unittest.mock import MagicMock, patch

from core.utils import load_i18n
from modules.export import export_model_logic


class TestExport(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch("core.bridge.requests.post")
    def test_export_model_stl_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Exported to path/test.stl"]}
        mock_post.return_value = mock_response

        res = export_model_logic("stl", "test", "en")

        self.assertIn("Exported to", res)
        params = mock_post.call_args[1]["json"]["payload"]["params"]
        script = mock_post.call_args[1]["json"]["payload"]["script"]
        self.assertEqual(params["filename"], "test")
        self.assertIn("createSTLExportOptions", script)

    @patch("core.bridge.requests.post")
    def test_export_model_step_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Exported to path/test.step"]}
        mock_post.return_value = mock_response

        res = export_model_logic("step", "test", "en")

        self.assertIn("Exported to", res)
        params = mock_post.call_args[1]["json"]["payload"]["params"]
        script = mock_post.call_args[1]["json"]["payload"]["script"]
        self.assertEqual(params["filename"], "test")
        self.assertIn("createSTEPExportOptions", script)

    @patch("core.bridge.requests.post")
    def test_export_model_f3d_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Exported to path/test.f3d"]}
        mock_post.return_value = mock_response

        res = export_model_logic("f3d", "test", "en")

        self.assertIn("Exported to", res)
        params = mock_post.call_args[1]["json"]["payload"]["params"]
        script = mock_post.call_args[1]["json"]["payload"]["script"]
        self.assertEqual(params["filename"], "test")
        self.assertIn("createFusionArchiveExportOptions", script)

    def test_export_model_rejects_unknown_format(self):
        res = export_model_logic("obj", "test", "en")
        self.assertEqual(res, "Error: Unsupported export format 'obj'. Supported formats: stl, f3d, step.")


if __name__ == "__main__":
    unittest.main()
