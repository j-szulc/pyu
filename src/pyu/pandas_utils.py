from typing import Dict, Callable
from .traceback import print_traceback

def __map_dict_worker(fun, ignore_errors=()):
    import pandas as pd
    i = 0
    def result(row):
        nonlocal i
        i += 1
        try:
            return pd.Series(fun(row.to_dict()))
        except Exception as e:
            if ignore_errors == "always" or any(ee in str(e) for ee in ignore_errors):
                import logging
                logging.error(f"Failed processing row {i} with the following exception:")
                print_traceback(e, logging_level=logging.ERROR)
                return pd.Series()
            else:
                raise e
    return result

def map_dict(fun: Callable[[Dict], Dict], df, include_original=True, ignore_errors=(), ignore_none=False):
    import pandas as pd
    if include_original:
        result = [df]
    else:
        result = []
    if ignore_none and ignore_errors != "always":
        ignore_errors = ignore_errors + ("'NoneType' object has no attribute",)
    result.append(df.apply(__map_dict_worker(fun, ignore_errors=ignore_errors), axis=1))
    return pd.concat(result, axis=1)
