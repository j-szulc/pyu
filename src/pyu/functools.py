from functools import wraps

def cache(fun):
    from dill import dumps
    from hashlib import sha256
    # TODO make it thread safe
    @wraps(fun)
    def result(*args, **kwargs):
        key = dumps((args, kwargs))
        key = sha256(key).hexdigest()
        if key not in result.cache:
            result.cache[key] = fun(*args, **kwargs)
        return result.cache[key]


def cache_once(filename, fun):
    from pathlib import Path
    from dill import dump, load
    if Path(filename).exists():
        with open(filename, "rb") as f:
            return load(f)
    result = fun()
    with open(filename, "wb") as f:
        dump(result, f)