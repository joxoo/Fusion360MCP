import unittest
from unittest.mock import MagicMock, patch
import json

import fusion_mcp_server
from modules.design import describe_tool_actions_logic


class TestApiProfiles(unittest.TestCase):
    @patch("fusion_mcp_server.register_tool")
    def test_compact_profile_registers_curated_public_api(self, mock_register_tool):
        mcp = MagicMock()

        fusion_mcp_server.register_compact_tools(mcp)

        registered = [call.args[1] for call in mock_register_tool.call_args_list]
        self.assertEqual(
            registered,
            [
                "manage_design",
                "describe_tool_actions",
                "analyze_design",
                "list_parameters",
                "edit_parameters",
                "create_sketch",
                "edit_sketch",
                "apply_3d_features",
                "edit_assembly",
                "edit_surfaces",
                "edit_forms",
                "import_mesh",
                "edit_mesh",
                "export_model",
            ],
        )

    @patch("fusion_mcp_server.register_thread_tools")
    @patch("fusion_mcp_server.register_mechanical_tools")
    @patch("fusion_mcp_server.register_export_tools")
    @patch("fusion_mcp_server.register_advanced_geometry_tools")
    @patch("fusion_mcp_server.register_form_tools")
    @patch("fusion_mcp_server.register_mesh_tools")
    @patch("fusion_mcp_server.register_surface_tools")
    @patch("fusion_mcp_server.register_sketch_tools")
    @patch("fusion_mcp_server.register_assembly_tools")
    @patch("fusion_mcp_server.register_parameter_tools")
    @patch("fusion_mcp_server.register_analysis_tools")
    @patch("fusion_mcp_server.register_geometry_tools")
    @patch("fusion_mcp_server.register_design_tools")
    def test_full_profile_registers_all_modules(
        self,
        mock_design,
        mock_geometry,
        mock_analysis,
        mock_parameters,
        mock_assembly,
        mock_sketch,
        mock_surfaces,
        mock_mesh,
        mock_forms,
        mock_advanced,
        mock_export,
        mock_mechanical,
        mock_threads,
    ):
        mcp = MagicMock()

        fusion_mcp_server.register_api_profile(mcp, "full")

        for mocked in (
            mock_design,
            mock_geometry,
            mock_analysis,
            mock_parameters,
            mock_assembly,
            mock_sketch,
            mock_surfaces,
            mock_mesh,
            mock_forms,
            mock_advanced,
            mock_export,
            mock_mechanical,
            mock_threads,
        ):
            mocked.assert_called_once_with(mcp)

    def test_describe_tool_actions_contains_extended_guidance(self):
        payload = json.loads(describe_tool_actions_logic("edit_surfaces"))
        guide = payload["edit_surfaces"]

        self.assertIn("actions", guide)
        self.assertIn("patch", guide["actions"])
        self.assertIn("stitch", guide["actions"])
        self.assertEqual(guide["actions"]["thicken"]["required"], ["body", "thick"])

    def test_describe_tool_actions_mesh_and_parameters_examples(self):
        mesh_payload = json.loads(describe_tool_actions_logic("edit_mesh"))
        param_payload = json.loads(describe_tool_actions_logic("edit_parameters"))

        self.assertIn("conv_type", mesh_payload["edit_mesh"]["actions"]["convert"]["example"])
        self.assertEqual(param_payload["edit_parameters"]["actions"]["set"]["required"], ["name", "expr"])


if __name__ == "__main__":
    unittest.main()
