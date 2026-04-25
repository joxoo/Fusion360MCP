import unittest
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

if __name__ == '__main__':
    unittest.main()
