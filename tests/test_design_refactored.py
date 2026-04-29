import unittest
from unittest.mock import MagicMock, patch
from modules.design import manage_design_logic
from core.utils import load_i18n

class TestDesign(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_manage_design_cleanup(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = manage_design_logic("cleanup", "en")
        self.assertEqual(res, "Design cleaned up.")

if __name__ == '__main__':
    unittest.main()
