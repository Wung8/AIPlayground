import ast

WHITELISTED_IMPORTS = {
    "math",
    "random",
    "numpy",
    "enum",
    "heapq",
}

BANNED_FUNCTIONS = {
    "exec",
    "eval",
    "compile",
    "open",
    "input",
    "globals",
    "locals",
    "vars",
    "dir",
    "getattr",
    "setattr",
    "delattr",
    "__import__",
    "__builtins__",
    "__package__",
    "__doc__",
    "__loader__",
    "__spec__",
    "__annotations__",
    "__build_class__",
    "__debug__",
    "__loader__",
    "object",
    "help",
    "memoryview"
}

class SecurityError(Exception):
    pass


class SecureVisitor(ast.NodeVisitor):
    def visit_Import(self, node):
        for alias in node.names:
            root = alias.name.split('.')[0]
            if root not in WHITELISTED_IMPORTS:
                raise SecurityError(f"Import of '{alias.name}' is not allowed")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            root = node.module.split('.')[0]
            if root not in WHITELISTED_IMPORTS:
                raise SecurityError(f"Import from '{node.module}' is not allowed")
        self.generic_visit(node)

    def visit_Call(self, node):
        # Detect direct function calls
        if isinstance(node.func, ast.Name):
            if node.func.id in BANNED_FUNCTIONS:
                raise SecurityError(f"Call to '{node.func.id}' is not allowed")

        # Detect attribute calls (e.g., os.system)
        if isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr
            if attr_name in BANNED_FUNCTIONS:
                raise SecurityError(f"Call to attribute '{attr_name}' is not allowed")

        self.generic_visit(node)


def check_bot(source_code: str):
    try:
        tree = ast.parse(source_code)
        SecureVisitor().visit(tree)
    except SecurityError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Parse error: {e}"

    return True, "Code is safe"