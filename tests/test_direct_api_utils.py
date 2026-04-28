import unittest

from core.direct_api_utils import should_auto_invoke_run


class TestDirectApiUtils(unittest.TestCase):
    def test_should_auto_invoke_run_for_definition_without_call(self):
        script = """
def run(context):
    print("hello")
"""
        self.assertTrue(should_auto_invoke_run(script))

    def test_should_not_auto_invoke_run_when_explicitly_called(self):
        script = """
def run(context):
    print("hello")

run(None)
"""
        self.assertFalse(should_auto_invoke_run(script))

    def test_should_not_auto_invoke_when_no_run_function_exists(self):
        self.assertFalse(should_auto_invoke_run("print('hello')"))


if __name__ == '__main__':
    unittest.main()
