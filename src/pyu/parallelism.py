def __pmap_tqdm_threads(fn, *iterables, n_jobs=1):
    from tqdm.contrib.concurrent import thread_map
    return thread_map(fn, *iterables, max_workers=n_jobs)

from tqdm.contrib.concurrent import thread_map as __pmap_tqdm_threads
from tqdm.contrib.concurrent import process_map as __pmap_tqdm_process

def __dill_worker(fun, *args, **kwargs):
    from dill import loads
    return loads(fun)(*args, **kwargs)
    
def __pmap_tqdm_process_dill(fn, *iterables, max_workers=None):
    from dill import dumps
    from itertools import repeat
    return __pmap_tqdm_process(__dill_worker, repeat(dumps(fn)), *iterables, max_workers=max_workers)

def __pmap_tqdm_threads_dill(fn, *iterables, max_workers=None):
    from dill import dumps
    from itertools import repeat
    return __pmap_tqdm_threads(__dill_worker, repeat(dumps(fn)), *iterables, max_workers=max_workers)

def pmap(fn, *iterables, max_workers=None, use_threads=False, use_dill=False):
    if use_dill:
        if use_threads:
            return __pmap_tqdm_threads_dill(fn, *iterables, max_workers=max_workers)
        else:
            return __pmap_tqdm_process_dill(fn, *iterables, max_workers=max_workers)
    else:
        if use_threads:
            return __pmap_tqdm_threads(fn, *iterables, max_workers=max_workers)
        else:
            return __pmap_tqdm_process(fn, *iterables, max_workers=max_workers)
