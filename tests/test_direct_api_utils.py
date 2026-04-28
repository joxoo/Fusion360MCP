import types
import unittest

from core.direct_api_utils import (
    ApplicationProxy,
    ScriptDialogError,
    UiMessageBoxProxy,
    patch_application_get,
    should_auto_invoke_run,
)


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

    def test_ui_message_box_proxy_raises_instead_of_opening_dialog(self):
        class DummyUi:
            def __init__(self):
                self.called = False

            def messageBox(self, text):
                self.called = True
                return text

        proxy = UiMessageBoxProxy(DummyUi())

        with self.assertRaises(ScriptDialogError) as cm:
            proxy.messageBox("Script failed")

        self.assertEqual(str(cm.exception), "Script failed")
        self.assertFalse(proxy._ui.called)

    def test_ui_message_box_proxy_delegates_other_attributes(self):
        class DummyUi:
            def __init__(self):
                self.commandDefinitions = "defs"

        proxy = UiMessageBoxProxy(DummyUi())
        self.assertEqual(proxy.commandDefinitions, "defs")

    def test_application_proxy_replaces_user_interface(self):
        class DummyApp:
            def __init__(self):
                self.version = "1.0"

        ui_proxy = UiMessageBoxProxy(type("DummyUi", (), {})())
        app_proxy = ApplicationProxy(DummyApp(), ui_proxy)

        self.assertIs(app_proxy.userInterface, ui_proxy)
        self.assertEqual(app_proxy.version, "1.0")

    def test_patch_application_get_redirects_application_lookup(self):
        class DummyUi:
            def messageBox(self, text):
                return text

        class DummyApp:
            def __init__(self):
                self.userInterface = DummyUi()

        original_app = DummyApp()
        proxied_ui = UiMessageBoxProxy(original_app.userInterface)
        proxied_app = ApplicationProxy(original_app, proxied_ui)
        adsk_module = types.SimpleNamespace(
            core=types.SimpleNamespace(
                Application=type("Application", (), {"get": staticmethod(lambda: original_app)})
            )
        )

        with patch_application_get(adsk_module, proxied_app):
            current_app = adsk_module.core.Application.get()
            self.assertIs(current_app, proxied_app)
            with self.assertRaises(ScriptDialogError):
                current_app.userInterface.messageBox("Blocked")

        self.assertIs(adsk_module.core.Application.get(), original_app)


if __name__ == '__main__':
    unittest.main()
