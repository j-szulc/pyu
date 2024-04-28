from typing import Callable
from pathlib import Path
import tee
from contextlib import contextmanager
import tempfile
import traceback as tb

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

def log_git(path="patch.txt"):
    import mlflow
    import git
    repo = git.Repo(search_parent_directories=True)
    try:
        hexsha = repo.head.object.hexsha
    except ValueError:
        hexsha = "No commits yet!"
    diff = repo.git.diff(None)
    def helper(target_path):
        with open(target_path, 'w') as f:
            f.write(f"Commit: {hexsha}\n")
            f.write(diff)
            f.write("\n")
    return log_through_file(helper, path)


@contextmanager
def log_std():
    import mlflow
    with tempfile.TemporaryDirectory() as tmpdirname:
        stdout_path = Path(tmpdirname) / 'stdout.log'
        stderr_path = Path(tmpdirname) / 'stderr.log'
        try:
            with tee.StdoutTee(stdout_path, buff=1), tee.StderrTee(stderr_path, buff=1):
                yield
        except Exception as e:
            with open(stderr_path, 'a') as f:
                tb.print_exc(file=f)
            raise e
        finally:
            mlflow.log_artifact(stdout_path)
            mlflow.log_artifact(stderr_path)

def log_metric(name, value, verbose=False): 
    import mlflow
    mlflow.log_metric(name, value)
    if verbose:
        print(f"{name}: {value}")

@contextmanager
def autolog(experiment_name=None):
    import mlflow
    if experiment_name is None:
        from unique_names_generator import get_random_name
        experiment_name = get_random_name()
    mlflow.set_experiment(experiment_name)
    mlflow.autolog()
    with mlflow.start_run(), log_std():
        try:
            log_git()
        except:
            pass
        yield