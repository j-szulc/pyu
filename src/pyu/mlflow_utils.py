from typing import Callable
from pathlib import Path
import tee
from contextlib import contextmanager
import tempfile
import traceback as tb

def log_through_file(filegen: Callable[[Path], None], path: Path, print_uid=False):
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
    artifact_uid = mlflow.get_artifact_uri(str((parent or Path("/")) / path.name))
    if print_uid:
        print(f"Artifact UID: {artifact_uid}")

def load_pickle(artifact_uid):
    import mlflow
    import pickle
    downloaded = mlflow.artifacts.download_artifacts(artifact_uid)
    return pickle.load(open(downloaded, 'rb'))


def log_glob(glob_pattern, dirpath=None):
    from glob import glob
    import mlflow
    for file in glob(glob_pattern):
        mlflow.log_artifact(file, dirpath)

def log_numpy(arr, path, print_uid=False):
    return log_through_file(arr.tofile, path, print_uid)

def log_git(path="patch.txt", print_uid=False):
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
    return log_through_file(helper, path, print_uid)

def log_pickle(obj, path, print_uid=False):
    import pickle
    return log_through_file(lambda path: pickle.dump(obj, open(path, 'wb')), path, print_uid)

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

def log_model(model, name=None, epoch=None, zfill=4, path="checkpoints", print_uid=False):
    import torch
    if name is None:
        name = model.__class__.__name__
    if epoch is not None:
        name += f"_{str(epoch).zfill(zfill)}"
    log_through_file(lambda path: torch.save(model.state_dict(), path), f"{path}/{name}.pt", print_uid)

def download_checkpoint(name, run_id="latest", epoch="latest", path="checkpoints"):
    import mlflow
    if run_id == "latest":
        run_id = mlflow.search_runs(order_by=["start_time"], max_results=1).iloc[0].run_id
    artifacts = mlflow.artifacts.list_artifacts(run_id=run_id, artifact_paths=path)
    artifact_paths = [artifact.path for artifact in artifacts]
    import re
    rgx = re.escape(name) + (r"_(\d+)\.pt" if epoch == "latest" else f"_{epoch}.pt")
    # Filter by name
    matches = {path: re.search(rgx, path) for path in artifact_paths}
    matches = {path: int(match.group(1)) for path, match in matches.items() if match}
    best_match = max(matches.items(), key=lambda kv:kv[1]) if matches else None
    if best_match is not None:
        path = best_match[0]
        return mlflow.artifacts.download_artifacts(artifact_path=path, run_id=run_id), best_match[1]

def load_checkpoint(model, name=None, run_id="latest", epoch="latest", path="checkpoints"):
    import torch
    if name is None:
        name = model.__class__.__name__
    download_path, epoch = download_checkpoint(name, run_id, epoch, path)
    if download_path is None:
        return
    checkpoint = torch.load(download_path, map_location=model.device)
    model.load_state_dict(checkpoint)
    return epoch
