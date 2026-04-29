import unittest
from unittest.mock import MagicMock, patch
from modules.parameters import edit_parameters_logic
from core.utils import load_i18n

class TestParameters(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_edit_parameters_batch(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["set:CREATED:width"]}
        mock_post.return_value = mock_response

        ops = [{"action": "set", "name": "width", "expr": "100 mm"}]
        res = edit_parameters_logic(ops, "en")
        self.assertEqual(res, "Parameters updated successfully.")

if __name__ == '__main__':
    unittest.main()
