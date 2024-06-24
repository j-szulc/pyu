from .lazy_type import LazyType
from .dispatch import SuperDispatchMethod
import logging
import pickle

def fallback_dump(obj, buf):
    logging.warning(f"Using fallback save (Pickle) for {obj.__class__}")
    pickle.dump(obj, buf)

dump = SuperDispatchMethod(fallback=fallback_dump)

@dump.register_type(str)
def _(obj,buf):
    buf.write(obj.encode())

@dump.register_type(bytes)
def _(obj,buf):
    buf.write(obj)

@dump.register_type(LazyType("torch.Tensor"))
def _(obj,buf):
    import torch
    torch.save(obj, buf)

@dump.register_type(LazyType("numpy.ndarray"))
def _(obj,buf):
    import numpy as np
    np.save(buf, obj)

@dump.register_type(LazyType("PIL.Image.Image"))
def _(obj,buf):
    obj.save(buf, "PNG")

@dump.register_type(dict)
@dump.register_type(list)
def _(obj,buf):
    import json
    buf.write(json.dumps(obj).encode())

def fallback_dumps(obj):
    from io import BytesIO
    buf = BytesIO()
    dump(obj, buf)
    buf.seek(0)
    return buf.read()

dumps = SuperDispatchMethod(fallback=fallback_dumps)
