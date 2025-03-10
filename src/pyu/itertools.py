def _get_len(obj, default=None):
    """Return an exact number of elements in the object, if possible, else default.
    """
    try:
        return len(obj)
    except TypeError:
        return default

def _get_qualname(obj):
    try:
        return obj.__qualname__
    except AttributeError:
        pass

def zip_strict(*args):
    lens = [_get_len(arg, default=None) for arg in args]
    if len(set(l for l in lens if l is not None)) > 1:
        lens_str = ", ".join(str(l) if l is not None else "unknown" for l in lens)
        raise ValueError(f"zip_strict: iterators have different lengths: {lens_str}!")
    args = [iter(arg) for arg in args]
    yield from zip(*args)
    for i, arg in enumerate(args):
        try:
            next(arg)
        except StopIteration:
            pass
        else:
            qualname = _get_qualname(arg)
            if qualname is None:
                qualname = repr(arg)
            raise ValueError(f"zip_strict: iterator {i}({qualname}) has more elements than the others")

def flatten(iterable):
    for elem in iterable:
        if isinstance(elem, (list, tuple)):
            yield from flatten(elem)
        else:
            yield elem