"""
Code package for policy model dataset generation and processing pipeline.
"""

def __getattr__(name):
    # Delegate missing attributes to the standard library 'code' module to prevent debugger conflicts
    import importlib.util
    import os
    import sys

    for p in sys.path:
        if p and p != "." and p != os.getcwd():
            candidate = os.path.join(p, "code.py")
            if os.path.isfile(candidate):
                spec = importlib.util.spec_from_file_location("_stdlib_code", candidate)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    val = getattr(mod, name)
                    globals()[name] = val
                    return val
    raise AttributeError(f"module 'code' has no attribute '{name}'")
