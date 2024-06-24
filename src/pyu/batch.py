
def process(fun, input_file, output_file, only_cache=False):
    from pathlib import Path
    import logging
    from .dump import dump
    output_file = Path(output_file)
    if output_file.exists():
        logging.debug(f"Skipping {fun.__name__}({input_file}) -> {output_file}")
        if only_cache:
            return True
        return
    if only_cache:
        return False
    temp_output_file = output_file.with_suffix(".incomplete")
    with open(temp_output_file, "wb") as f:
        result = fun(input_file)
        dump(result, f)
    temp_output_file.rename(output_file)

def batch_process(fun, root_dir, input_glob="./**/*", output_suffix=".out"):
    from pathlib import Path
    import logging
    from tqdm import tqdm
    root_dir = Path(root_dir)
    to_process = []
    for input_file in root_dir.rglob(input_glob):
        if input_file.is_dir():
            continue
        output_file = input_file.with_suffix(output_suffix)
        if not process(fun, input_file, output_file, only_cache=True):
            to_process.append((input_file, output_file))
    for input_file, output_file in tqdm(to_process):
        logging.debug(f"Processing {input_file} -> {output_file}")
        process(fun, input_file, output_file)

def get_duplicates(l):
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

    in_files_duplicates = get_duplicates(in_files)
    assert not in_files_duplicates, f"Input files have duplicates: {in_files_duplicates}"
    out_files_duplicates = get_duplicates(out_files)
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


def simple_batch_rename(root_dir, filter_glob="./**/*", no_dirs=True, new_suffix=None, dry_run=False, **kwargs):
    from pathlib import Path
    root_dir = Path(root_dir).absolute()

    import re
    PARENT_OVERRIDE_RE = re.compile(r"p(\d+)")
    def map_kwargs(k):
        m = PARENT_OVERRIDE_RE.match(k)
        assert m, "Kwargs must be of the form p<parent_number>=<new_parent_name>"
        result = int(m.group(1))-1
        assert result >= 0, "Parent numbers must be positive!"
        return result
    kwargs = {map_kwargs(k): v for k, v in kwargs.items()}

    in_files = list(Path(root_dir).rglob(filter_glob))
    if no_dirs:
        in_files = [f for f in in_files if not f.is_dir()]
    out_files = in_files
    if new_suffix is not None:
        out_files = [f.with_suffix(new_suffix) for f in out_files]

    out_files_parts = {f: list(f.absolute().relative_to(root_dir).parts[:-1])for f in out_files}
    for f in out_files_parts:
        parts = out_files_parts[f]
        for i, new_parent in kwargs.items():
            assert len(parts) > i, f"Parent {i} does not exist for {f}, parents: {parts}"
            parts[i] = new_parent
        out_files_parts[f] = [p for p in parts if p]

    out_files = [Path(root_dir).joinpath(*parts, f.name) for f, parts in out_files_parts.items()]
    batch_rename(in_files, out_files, dry_run=dry_run)
