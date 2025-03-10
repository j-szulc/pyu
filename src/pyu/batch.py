from .parallelism import pmap
from .traceback import print_traceback

def __temp_in_working_dir(path, label="temp"):
    return path.with_suffix(f".{label}{path.suffix}")

def __process(fun, input_file, output_file, output_file_arg=False, ignore_errors=True):
    from dill import dump
    temp_output_file = __temp_in_working_dir(output_file, "incomplete")
    temp_output_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        if output_file_arg:
            fun(input_file, temp_output_file)
        else:
            with open(temp_output_file, "wb") as f:
                result = fun(input_file)
                dump(result, f)
        temp_output_file.rename(output_file)
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        if not ignore_errors:
            raise e
        import logging
        logging.error(f"Failed processing {input_file} -> {output_file} with the following exception:")
        print_traceback(e, logging_level=logging.ERROR)
    finally:
        # TODO - try catch
        if temp_output_file.exists():
            temp_output_file.unlink()

def batch_process(fun, root_dir, input_ext=None, input_glob="./**/*", output_suffix=".out", output_file_arg=False, new_root_dir=None, max_workers=None, **kwargs):
    from pathlib import Path
    import logging
    from tqdm import tqdm
    root_dir = Path(root_dir)
    if new_root_dir:
        new_root_dir = Path(new_root_dir)
        new_root_dir.mkdir(parents=True, exist_ok=True)
    if input_ext and not input_ext.startswith("."):
        input_ext = "." + input_ext
    to_process = []
    all_output_files = []
    for input_file in root_dir.rglob(input_glob):
        if input_file.is_dir():
            continue
        if input_ext and input_file.suffix != input_ext:
            continue
        output_file = input_file.with_suffix(output_suffix)
        all_output_files.append(output_file)
        if new_root_dir:
            output_file = new_root_dir / output_file.relative_to(root_dir)
        if output_file.exists():
            logging.debug(f"Skipping {input_file} -> {output_file}, output already exists")
        else:
            to_process.append((input_file, output_file))
    if max_workers is None:
        for input_file, output_file in tqdm(to_process):
            logging.debug(f"Processing {input_file} -> {output_file}")
            __process(fun, input_file, output_file, output_file_arg=output_file_arg)
    elif to_process:
        pmap(lambda in_, out: __process(fun, in_, out, output_file_arg, **kwargs), *zip(*to_process), max_workers=max_workers, use_dill=True)
    return all_output_files

def __get_duplicates(l):
    from collections import defaultdict
    l_counts = defaultdict(int)
    for x in l:
        l_counts[x] += 1
    return {x: c  for x, c in l_counts.items() if c > 1}

def batch_rename(in_files, out_files, dry_run=False):
    from pathlib import Path
    import logging
    from tqdm import tqdm

    in_files = [Path(f).absolute() for f in in_files]
    out_files = [Path(f).absolute() for f in out_files]
    assert len(in_files) == len(out_files), "Input and output file lists must be the same length"
    intersect = set(in_files) & set(out_files)
    assert not intersect, f"Input and output file lists must not intersect: {intersect}"

    in_files_duplicates = __get_duplicates(in_files)
    assert not in_files_duplicates, f"Input files have duplicates: {in_files_duplicates}"
    out_files_duplicates = __get_duplicates(out_files)
    assert not out_files_duplicates, f"Output files have duplicates: {out_files_duplicates}"

    for in_file, out_file in zip(in_files, out_files):
        assert in_file.exists(), f"{in_file} does not exist!"
        assert not out_file.exists(), f"{out_file} already exists!"

    for in_file, out_file in tqdm(zip(in_files, out_files)):
        printer = print if dry_run else logging.debug
        printer(f"Renaming {in_file} -> {out_file}")
        if not dry_run:
            out_file.parent.mkdir(parents=True, exist_ok=True)
            in_file.rename(out_file)

def lambda_batch_rename(root_dir, rename_fun, filter_glob="./**/*", filter_out_dirs=True, filter_out_files=False, dry_run=False):
    from pathlib import Path
    root_dir = Path(root_dir).absolute()

    in_files = list(Path(root_dir).rglob(filter_glob))
    if filter_out_dirs and filter_out_files:
        import logging
        logging.warning("Filtering out everything!")
    if filter_out_dirs:
        in_files = [f for f in in_files if not f.is_dir()]
    if filter_out_files:
        in_files = [f for f in in_files if f.is_dir()]
    out_files = in_files
    if not isinstance(rename_fun, list):
        rename_fun = [rename_fun]
    assert rename_fun, "No renaming functions specified!"
    for fun in rename_fun:
        out_files = [fun(f) for f in out_files]

    batch_rename(in_files, out_files, dry_run=dry_run)

def simple_batch_rename(root_dir, filter_glob="./**/*", filter_out_dirs=True, filter_out_files=False, dry_run=False, new_suffix=None, **kwargs):

    if not (kwargs or new_suffix):
        import logging
        logging.warning("No renaming specified!")
        return

    rename_fun_list = []
    def override_suffix(f):
        return f.with_suffix(new_suffix)
    if new_suffix:
        rename_fun_list.append(override_suffix)

    import re
    PARENT_OVERRIDE_RE = re.compile(r"p(\d+)")
    def map_kwargs(k):
        m = PARENT_OVERRIDE_RE.match(k)
        assert m, "Kwargs must be of the form p<parent_number>=<new_parent_name>"
        result = int(m.group(1))-1
        assert result >= 0, "Parent numbers must be positive!"
        return result
    kwargs = {map_kwargs(k): v for k, v in kwargs.items()}

    from pathlib import Path
    def override_parent(f):
        parts = list(f.parts)
        for i, new_parent in kwargs.items():
            assert len(parts) > i, f"Parent {i} does not exist for {f}, parents: {parts}"
            parts[i] = new_parent
        return Path.joinpath(*[p for p in parts if p], f.name)
    if kwargs:
        rename_fun_list.append(override_parent)

    lambda_batch_rename(root_dir, rename_fun_list, filter_glob=filter_glob, filter_out_dirs=filter_out_dirs, filter_out_files=filter_out_files, dry_run=dry_run)

from functools import wraps
def catch(fun):
    @wraps(fun)
    def catch_fun(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except Exception as e:
            import logging
            logging.error(f"Failed processing {fun} with the following exception:")
            print_traceback(e, logging_level=logging.ERROR)
    return catch_fun
# def delayed(fun):
#     @wraps(fun)
#     def delayed_fun(*args, **kwargs):
#         return lambda: fun(*args, **kwargs)
#     return delayed_fun

# def map_verbose(funs, desc=None, total=None, **kwargs):
#     from tqdm import tqdm
#     if desc is None and funs:
#         desc = funs[0].__name__
#     errors = []
#     for fun in tqdm(funs, desc=desc, total=total):
#         try:
#             yield fun()
#         except Exception as e:
#             import logging
#             logging.error(f"Failed processing {fun} with the following exception:")
#             print_traceback(e, logging_level=logging.ERROR)
#             errors.append((fun, e))
#     if errors:
#         print(f"Got {len(errors)} errors.")