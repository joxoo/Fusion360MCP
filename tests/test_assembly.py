import unittest
from unittest.mock import MagicMock, patch
from modules.assembly import create_component_logic, create_joint_logic

class TestAssembly(unittest.TestCase):
    @patch('core.bridge.requests.post')
    def test_create_component_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["Motor"]}
        mock_post.return_value = mock_response

        res = create_component_logic("Motor", "en")
        self.assertEqual(res, "Component 'Motor' created.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['name'], "Motor")
        
    def test_component_activation_script(self):
        from modules.assembly_scripts import build_create_component_script
        script = build_create_component_script()
        self.assertIn("occ.activate()", script)
        self.assertIn("target = resolve_component_context", script)

    @patch('core.bridge.requests.post')
    def test_create_joint_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": ["OK"]}
        mock_post.return_value = mock_response

        res = create_joint_logic("Comp1", "Comp2", "Revolute", "en")
        self.assertEqual(res, "Joint (Revolute) created.")
        params = mock_post.call_args[1]['json']['payload']['params']
        self.assertEqual(params['c1'], "Comp1")
        self.assertEqual(params['c2'], "Comp2")
        self.assertEqual(params['type'], "Revolute")

if __name__ == '__main__':
    unittest.main()
