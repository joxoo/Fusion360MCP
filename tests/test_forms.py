import unittest
from unittest.mock import MagicMock, patch
from modules.forms import edit_forms_logic
from core.utils import load_i18n

class TestForms(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_edit_forms_batch(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["extrude:OK:Form1"]}
        mock_post.return_value = mock_response

        ops = [{"action": "extrude", "sketch": "Sketch1", "dist": 5.0}]
        res = edit_forms_logic(ops, "en")
        self.assertEqual(res, "Forms (T-Splines) updated successfully.")

if __name__ == '__main__':
    unittest.main()
