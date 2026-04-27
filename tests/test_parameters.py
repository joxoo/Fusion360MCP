import unittest
from unittest.mock import MagicMock, patch
from modules.parameters import (
    manage_parameter_logic,
    list_parameters_logic,
    delete_parameter_logic
)

class TestParameters(unittest.TestCase):
    @patch('core.bridge.requests.post')
    def test_manage_parameter_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["CREATED"]}
        mock_post.return_value = mock_response

        res = manage_parameter_logic("Thickness", "5mm", "mm", "Base thickness", "en")
        self.assertEqual(res, "Parameter 'Thickness' created.")

    @patch('core.bridge.requests.post')
    def test_list_parameters_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ['[{"name": "P1", "expression": "10"}]']}
        mock_post.return_value = mock_response

        res = list_parameters_logic("en")
        self.assertIn('"name": "P1"', res)

    @patch('core.bridge.requests.post')
    def test_delete_parameter_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = delete_parameter_logic("P1", "en")
        self.assertEqual(res, "Parameter 'P1' successfully deleted.")

if __name__ == '__main__':
    unittest.main()
