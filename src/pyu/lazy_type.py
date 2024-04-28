
def LazyType(type_full_path):
    """
    Allows testing for 'isinstance' without importing the module.
    For example:
    t = LazyType("numpy.ndarray")
    print(isinstance(1, t)) # False - happens without importing numpy
    import numpy as np
    a = np.ndarray((1, 2, 3))
    print(isinstance(a, t)) # True - now numpy is imported
    """
    args = type_full_path.rsplit(".", 1)
    if len(args) == 1:
        args = ("builtins", args[0])
    module_name, backend_type_str = args
    module_parts = module_name.split(".")
    module_prefixes = [".".join(module_parts[:i]) for i in range(1, len(module_parts) + 1)]
    backend_type = None

    def try_import():
        """
        Finally imports the "module_name.backend_type_str"
        """
        nonlocal backend_type
        if backend_type is not None:
            return # already imported
        import sys
        if all(prefix not in sys.modules for prefix in module_prefixes):
            return # module not imported anywhere else, no need to import here
        import importlib
        try:
            m = importlib.import_module(module_name)
            backend_type = getattr(m, backend_type_str)
        except ImportError | AttributeError:
            import warnings
            from traceback import format_exc
            warnings.warn(f"{format_exc()}\nCould not import {type_full_path}!")
            return  # could not import

    class LazyTypeInstanceMeta(type):

        def __instancecheck__(self, instance):
            try_import()
            if backend_type is None:
                return False
            return isinstance(instance, backend_type)

    class LazyTypeInstance(metaclass=LazyTypeInstanceMeta):

        def _debug():
            return backend_type, module_name, backend_type_str
        pass

    return LazyTypeInstance