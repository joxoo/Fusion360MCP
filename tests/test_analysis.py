import unittest
from unittest.mock import MagicMock, patch
from modules.analysis import analyze_design_logic
from core.utils import load_i18n

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        load_i18n()

    @patch('core.bridge.requests.post')
    def test_analyze_design_validate(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ['{"body_count": 1}']}
        mock_post.return_value = mock_response

        res = analyze_design_logic("validate", "en")
        self.assertEqual(res, '{"body_count": 1}')

if __name__ == '__main__':
    unittest.main()
