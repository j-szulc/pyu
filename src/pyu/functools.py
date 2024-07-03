
def cache_once(filename, fun):
    from pathlib import Path
    from dill import dump, load
    if Path(filename).exists():
        with open(filename, "rb") as f:
            return load(f)
    result = fun()
    with open(filename, "wb") as f:
        dump(result, f)