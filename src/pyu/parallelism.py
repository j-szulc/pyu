from tqdm.contrib.concurrent import thread_map as __pmap_tqdm_threads
from tqdm.contrib.concurrent import process_map as __pmap_tqdm_process
from dataclasses import dataclass

@dataclass
class MaybePickled:
    obj: object
    # TODO make it nice
    pickled: bool = False
    use_dill: bool = False

    def from_obj(obj, use_dill=False):
        if use_dill:
            from dill import dumps
        else:
            from pickle import dumps
        try:
            return MaybePickled(dumps(obj), True, use_dill=use_dill)
        except TypeError:
            return MaybePickled(obj, False,)

    def to_obj(self):
        if self.pickled:
            if self.use_dill:
                from dill import loads
            else:
                from pickle import loads
            return loads(self.obj)
        else:
            return self.obj


def __dill_worker(fun, *args, **kwargs):
    args = [arg.to_obj() if isinstance(arg, MaybePickled) else arg for arg in args]
    kwargs = {k: v.to_obj() if isinstance(v, MaybePickled) else v for k, v in kwargs.items()}
    from dill import loads
    return loads(fun)(*args, **kwargs)

def __pmap_tqdm_process_dill(fn, *iterables, max_workers=None):
    from dill import dumps
    from itertools import repeat
    return __pmap_tqdm_process(__dill_worker, repeat(dumps(fn)), *[[MaybePickled.from_obj(obj, use_dill=True) for obj in it] for it in iterables], max_workers=max_workers)

def __pmap_tqdm_threads_dill(fn, *iterables, max_workers=None):
    from dill import dumps
    from itertools import repeat
    return __pmap_tqdm_threads(__dill_worker, repeat(dumps(fn)), *[[MaybePickled.from_obj(obj, use_dill=True) for obj in it] for it in iterables], max_workers=max_workers)

def pmap(fn, *iterables, max_workers=None, use_threads=False, use_dill=False):
    import logging
    if not iterables:
        logging.warning(f"Tried to parallelize function {fn.__name__} over an empty iterable!")
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

def __call(fn):
    return fn()

def pmap_zeroarg(fns, max_workers=None, use_threads=False, use_dill=False):
    return pmap(__call, fns, max_workers=max_workers, use_threads=use_threads, use_dill=use_dill)

def __delayed_worker(fn, args, kwargs):
    return fn()(*args, **kwargs)

def pmap_delayed(delayed_fns, max_workers=None, use_threads=False, use_dill=False):
    fns, argss, kwargss = zip(*delayed_fns)
    return pmap(__delayed_worker, fns, argss, kwargss, max_workers=max_workers, use_threads=use_threads, use_dill=use_dill)