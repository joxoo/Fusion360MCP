import unittest
from core.utils import format_response, get_tool_definition

class TestUtils(unittest.TestCase):
    def test_format_response_en(self):
        res = format_response("en", "Hallo {name}", "Hello {name}", name="World")
        self.assertEqual(res, "Hello World")

    def test_format_response_de(self):
        res = format_response("de", "Hallo {name}", "Hello {name}", name="World")
        self.assertEqual(res, "Hallo World")

    def test_get_tool_definition(self):
        mock_i18n = {
            "de": {"tools": {"test": {"name": "test_de", "description": "desc_de"}}},
            "en": {"tools": {"test": {"name": "test_en", "description": "desc_en"}}}
        }
        de, en = get_tool_definition(mock_i18n, "test")
        self.assertEqual(de["name"], "test_de")
        self.assertEqual(en["name"], "test_en")

if __name__ == '__main__':
    unittest.main()
