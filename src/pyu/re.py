
def maybe_group(match, group):
    if match is None:
        return None
    try:
        return match.group(group)
    except IndexError:
        return None

def maybe_compile(pattern):
    import re
    if isinstance(pattern, str):
        return re.compile(pattern)
    return pattern
