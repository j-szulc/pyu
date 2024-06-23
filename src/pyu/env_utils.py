from contextlib import contextmanager
import os

@contextmanager
def override_env(**kwargs):
    old = {}
    for key, value in kwargs.items():
        if key in os.environ:
            old[key] = os.environ[key]
        os.environ[key] = value
    yield
    for key, value in kwargs.items():
        if key in old:
            os.environ[key] = old[key]
        else:
            del os.environ[key]