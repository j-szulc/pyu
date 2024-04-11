from typing import Callable
from pathlib import Path
import tee
from contextlib import contextmanager
import tempfile

def log_through_file(filegen: Callable[[Path], None], path: Path):
    import mlflow
    path = Path(path)
    parent = path.parent
    # Check if root
    if parent.parent == parent:
        parent = None
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpfile = Path(tmpdirname) / path.name
        filegen(tmpfile)
        mlflow.log_artifact(tmpfile, parent)

def log_glob(glob_pattern, dirpath=None):
    from glob import glob
    import mlflow
    for file in glob(glob_pattern):
        mlflow.log_artifact(file, dirpath)

def log_numpy(arr, path):
    return log_through_file(arr.tofile, path)

@contextmanager
def log_std():
    import mlflow
    with tempfile.TemporaryDirectory() as tmpdirname:
        stdout_path = Path(tmpdirname) / 'stdout.log'
        stderr_path = Path(tmpdirname) / 'stderr.log'
        try:
            with tee.StdoutTee(stdout_path, buff=1), tee.StderrTee(stderr_path, buff=1):
                yield
        finally:
            mlflow.log_artifact(stdout_path)
            mlflow.log_artifact(stderr_path)