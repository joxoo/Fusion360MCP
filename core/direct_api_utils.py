import ast
from contextlib import contextmanager


class _TopLevelRunCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.scope_depth = 0
        self.has_top_level_run_call = False

    def visit_FunctionDef(self, node):
        self.scope_depth += 1
        self.generic_visit(node)
        self.scope_depth -= 1

    def visit_AsyncFunctionDef(self, node):
        self.scope_depth += 1
        self.generic_visit(node)
        self.scope_depth -= 1

    def visit_ClassDef(self, node):
        self.scope_depth += 1
        self.generic_visit(node)
        self.scope_depth -= 1

    def visit_Call(self, node):
        if self.scope_depth == 0 and isinstance(node.func, ast.Name) and node.func.id == "run":
            self.has_top_level_run_call = True
        self.generic_visit(node)


def should_auto_invoke_run(script: str) -> bool:
    """Return True when the script defines top-level run() but never calls it."""
    try:
        tree = ast.parse(script)
    except SyntaxError:
        return False

    defines_run = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "run"
        for node in tree.body
    )
    if not defines_run:
        return False

    visitor = _TopLevelRunCallVisitor()
    visitor.visit(tree)
    return not visitor.has_top_level_run_call


class ScriptDialogError(RuntimeError):
    """Raised when a script tries to open a UI dialog during MCP execution."""


class UiMessageBoxProxy:
    """Delegates all UI access except modal dialogs, which are converted to errors."""

    def __init__(self, ui):
        self._ui = ui

    def messageBox(self, text, *args, **kwargs):
        raise ScriptDialogError(str(text))

    def __getattr__(self, name):
        return getattr(self._ui, name)


class ApplicationProxy:
    """Delegates Application access while replacing userInterface with a safe proxy."""

    def __init__(self, app, ui_proxy):
        self._app = app
        self.userInterface = ui_proxy

    def __getattr__(self, name):
        return getattr(self._app, name)


@contextmanager
def patch_application_get(adsk_module, app_proxy):
    """Temporarily patch adsk.core.Application.get to return the proxied app."""
    original_get = adsk_module.core.Application.get
    adsk_module.core.Application.get = staticmethod(lambda: app_proxy)
    try:
        yield
    finally:
        adsk_module.core.Application.get = original_get
