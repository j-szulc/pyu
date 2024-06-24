
def update(pip=True):
    if pip:
        import os
        os.system("pip install git+https://github.com/j-szulc/pyu.git")
    import importlib
    import pyu
    import pkgutil
    pkgs = [f"pyu.{m.name}" for m in pkgutil.iter_modules(pyu.__path__)]
    importlib.reload(pyu)
    for pkg in pkgs:
        import sys
        if pkg not in sys.modules:
            continue
        print(f"Reloading {pkg}")
        importlib.reload(importlib.import_module(pkg))
