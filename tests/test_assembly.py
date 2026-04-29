import unittest
from unittest.mock import MagicMock, patch
from modules.assembly import edit_assembly_logic
from core.utils import load_i18n

class TestAssembly(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_edit_assembly_batch(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["create_component:OK:Comp1"]}
        mock_post.return_value = mock_response

        ops = [{"action": "create_component", "name": "Comp1"}]
        res = edit_assembly_logic(ops, "en")
        self.assertEqual(res, "Assembly updated successfully.")

if __name__ == '__main__':
    unittest.main()
