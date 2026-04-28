import ast


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
