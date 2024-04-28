from .dispatch import SuperDispatchMethod
from .lazy_type import LazyType
import icecream

INDENT = 4
MAX_CHILDREN_PRINT = 3
MAX_CHILDREN_DICT_PRINT = 10
MAX_CHILDREN_BASIC = 10
MAX_CHAR_BASIC_STR = 100

def indent(text, spaces=INDENT):
    return "\n".join(" " * spaces + line for line in text.split("\n"))

def default_argumentToString(obj, recurse=None):
    s =icecream.DEFAULT_ARG_TO_STRING_FUNCTION(obj)
    s = s.replace('\\n', '\n')  # Preserve string newlines in output.
    return s

def register_printers(target: SuperDispatchMethod):

    def helper(root, children, max_children=MAX_CHILDREN_PRINT):
        from itertools import islice
        children = list(islice(children, max_children+1))
        exceeds = len(children) > max_children
        children = children[:max_children]
        lines = [indent(target(child)) for child in children]
        if exceeds:
            lines[-1] += " ..."
        return root + "\n" + "\n".join(lines)

    def is_basic(obj):
        if isinstance(obj, dict):
            return len(obj) < MAX_CHILDREN_BASIC and all(is_basic(k) and is_basic(v) for k, v in obj.items())
        if isinstance(obj, list) or isinstance(obj, tuple):
            return len(obj) < MAX_CHILDREN_BASIC and all(is_basic(x) for x in obj)
        if isinstance(obj, str):
            return len(obj) < MAX_CHAR_BASIC_STR
        return isinstance(obj, (int, float, bool))

    from typing import Iterable
    @target.register_type(Iterable)
    def _(arg, recurse=True):
        try:
            length = len(arg)
        except TypeError:
            length = "unknown"
        top = f"{type(arg).__name__}(length={length})"
        if not recurse:
            return top
        return helper(top, arg)
    
    from typing import Generator
    @target.register_type(Generator)
    def _(arg, recurse=True):
        top = "Generator"
        if not recurse:
            return top
        children = []
        for i, x in enumerate(arg):
            children.append(x)
            if i >= MAX_CHILDREN_PRINT:
                break
        import warnings
        warnings.warn(f"Consumed {len(children)} items from generator.")
        return helper(top, children, max_children=MAX_CHILDREN_PRINT)
        

    @target.register_type(LazyType("torch.Tensor"))
    def _(arg, recurse=None):
        return f"Tensor(shape={arg.shape}, dtype={arg.dtype})"

    @target.register_type(LazyType("numpy.ndarray"))
    def _(arg, recurse=None):
        return f"ndarray(shape={arg.shape}, dtype={arg.dtype})"
    
    @target.register_type(LazyType("PIL.Image.Image"))
    def _(arg, recurse=None):
        return f"Image(size={arg.size}, mode={arg.mode})"

    from dataclasses import dataclass
    from typing import Any
    @dataclass
    class DictItem:
        key: str
        value: Any

    @target.register_type(DictItem)
    def _(arg, recurse=True):
        return f"{target(arg.key, recurse=False)}: {target(arg.value, recurse=recurse)}"

    @target.register_type(dict)
    def _(arg, recurse=True):
        top = f"dict(length={len(arg)})"
        if not recurse:
            return top
        return helper(top, map(lambda kv: DictItem(*kv), arg.items()), max_children=MAX_CHILDREN_DICT_PRINT)

    @target.register_cond(is_basic)
    def _(arg, recurse=None):
        result = target.fallback(arg, recurse=recurse)
        if len(result) > MAX_CHAR_BASIC_STR:
            result = result[:MAX_CHAR_BASIC_STR] + " ..."
        return result

__argumentToString = SuperDispatchMethod(fallback=default_argumentToString)
register_printers(__argumentToString)
ic = icecream.IceCreamDebugger(argToStringFunction=__argumentToString)

def include_context(val=True):
    ic.configureOutput(includeContext=val)

def f():
    for i in range(10):
        yield i

t = f()
ic(t)
ic(t)