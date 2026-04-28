import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from modules.design import (
    direct_api_access_logic,
    cleanup_design_logic,
    create_new_design_logic,
    restart_mcp_logic,
    list_mcp_tools_logic,
    register_design_tools
)

class TestDesignRefactored(unittest.IsolatedAsyncioTestCase):
    @patch('core.bridge.requests.post')
    def test_direct_api_access_joins_output(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Simulate multi-line data returned from Fusion (including print statements)
        mock_response.json.return_value = {"status": "success", "data": ["Line 1", "Line 2", "Result OK"]}
        mock_post.return_value = mock_response

        res = direct_api_access_logic("print('test')", "en")
        
        # Verify that data is joined by newlines (User proposal fix)
        self.assertEqual(res, "Line 1\nLine 2\nResult OK")

    @patch('core.bridge.requests.post')
    def test_direct_api_access_returns_detail_when_no_data(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": [],
            "detail": "Auto-invoked run(context=None)."
        }
        mock_post.return_value = mock_response

        res = direct_api_access_logic("def run(context): pass", "en")

        self.assertEqual(res, "Auto-invoked run(context=None).")

    @patch('core.bridge.requests.post')
    def test_cleanup_design_uses_builder(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = cleanup_design_logic("en")
        self.assertEqual(res, "Design cleaned up.")
        
        # Verify script content from builder was sent
        sent_script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("root.occurrences.item(i).deleteMe()", sent_script)

    @patch('core.bridge.requests.post')
    def test_create_new_design_logic(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = create_new_design_logic("en")
        self.assertEqual(res, "New document created.")
        sent_script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("app.documents.add(0)", sent_script)

    @patch('core.bridge.requests.post')
    def test_restart_mcp_logic(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = restart_mcp_logic("en")
        self.assertEqual(res, "MCP restart command sent.")
        sent_script = mock_post.call_args[1]['json']['payload']['script']
        self.assertIn("start_mcp_server()", sent_script)

    async def test_list_mcp_tools_logic(self):
        # 1. Setup MCP Mock
        mock_mcp = MagicMock()
        tool1 = MagicMock(); tool1.name = "apple"; tool1.description = "desc1"
        tool2 = MagicMock(); tool2.name = "banana"; tool2.description = "desc2"
        
        # FastMCP.list_tools is async
        mock_mcp.list_tools = AsyncMock(return_value=[tool1, tool2])
        
        # 2. Register to set global _mcp_instance
        register_design_tools(mock_mcp)
        
        # 3. Call logic
        res = await list_mcp_tools_logic("en")
        
        self.assertIn("Registered Fusion360 MCP Tools:", res)
        self.assertIn("- apple: desc1", res)
        self.assertIn("- banana: desc2", res)
        
    async def test_list_mcp_tools_no_init(self):
        # Reset global instance for this test
        with patch('modules.design._mcp_instance', None):
            res = await list_mcp_tools_logic("en")
            self.assertEqual(res, "Error: MCP instance not initialized.")

if __name__ == '__main__':
    unittest.main()
