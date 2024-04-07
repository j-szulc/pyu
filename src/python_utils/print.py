def _get_shape(obj):
    try:
        return obj.shape
    except AttributeError:
        pass


def _get_len(obj):
    try:
        return len(obj)
    except TypeError:
        pass

def clip_str(s, max_len=100):
    if len(s) > max_len:
        return s[:max_len-3] + "..."
    return s

def describe(*obj):
    if len(obj) == 1:
        obj = obj[0]
    current_prefix = tuple()
    prefixes = []
    descriptions = []

    def describe_(obj):
        nonlocal current_prefix
        recurse = (isinstance(obj, list) or isinstance(obj, tuple))
        shape = _get_shape(obj)
        len_ = _get_len(obj)
        if (shape is None and len_ is None) and not recurse:
            value_str = clip_str(repr(obj), 20)
        elif isinstance(obj, str):
            value_str = clip_str(f'"{obj}"', 20)
        else:
            value_str = None
        type_str = repr(type(obj).__name__).strip("'")
        type_str = f"type={type_str}"
        if shape is not None:
            shape_str = f'shape={shape}'
        elif len_ and recurse:
            shape_str = f'containing {len_} elements:'
        elif len_ is not None:
            shape_str = f'length={len_}'
        elif recurse:
            shape_str = f'containing elements:'
        else:
            shape_str = None
        final_str = ", ".join(s for s in [value_str, type_str, shape_str] if s is not None)
        descriptions.append(final_str)
        prefixes.append(current_prefix)
        if recurse:
            for i, subobj in enumerate(obj):
                current_prefix = (*current_prefix, i)
                describe_(subobj)
                current_prefix = tuple(list(current_prefix)[:-1])

    describe_(obj)
    from itertools import zip_longest
    max_col_lens = [max(len(str(c)) for c in col) for col in zip_longest(*prefixes, fillvalue="")]
    prefix_total_len = sum(cl+2 for cl in max_col_lens)
    for prefix, desc in zip(prefixes, descriptions):
        prefix_str = ""
        for max_col_len, col_val in zip(max_col_lens, prefix):
            col_val = str(col_val).rjust(max_col_len)
            prefix_str += f"[{col_val}]"
        prefix_str = prefix_str.ljust(prefix_total_len)
        level_indent = " " * (len(prefix)*4)
        print(f"{prefix_str} {level_indent}{desc}")
