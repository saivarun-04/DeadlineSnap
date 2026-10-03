"""Smoke test: verify every name imported in app.py exists in its target module."""

import ast
import importlib
import sys
import unittest


class TestImports(unittest.TestCase):
    """Ensure all imported names are actually defined in their target modules."""

    def _get_imported_names(self, filepath: str) -> list[tuple[str, str]]:
        """Return [(local_name, module_name), ...] for all imported names."""
        tree = ast.parse(open(filepath, encoding="utf-8").read())
        results = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    local = alias.asname or alias.name
                    results.append((local, node.module))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    local = alias.asname or alias.name
                    # For bare imports like 'import core', local==module
                    results.append((local, alias.name))
        return results

    def _module_has(self, module_name: str, attr_name: str) -> bool:
        """Check whether *module_name* exposes *attr_name*."""
        try:
            mod = importlib.import_module(module_name)
            return hasattr(mod, attr_name)
        except Exception as exc:
            self.fail(f"Could not import {module_name!r}: {exc}")

    def test_all_app_imports_exist(self):
        """Every name imported in app.py must exist in its target module."""
        imports = self._get_imported_names("app.py")
        seen = {}
        for local, module in imports:
            # Skip stdlib / third-party modules we don't own
            if module in ("streamlit", "google", "google.genai", "typing",
                          "email", "email.mime", "email.mime.base",
                          "email.mime.multipart", "email.mime.text",
                          "datetime", "json", "smtplib", "ssl", "time", "uuid"):
                continue
            key = (local, module)
            if key in seen:
                continue
            seen[key] = True
            # For bare imports like `import core`, `import prompts`,
            # `local == module` means the module itself is imported — always valid.
            if local == module:
                continue
            self.assertTrue(
                self._module_has(module, local),
                f"app.py imports '{local}' from '{module}' but '{module}.{local}' does not exist",
            )


if __name__ == "__main__":
    unittest.main()
