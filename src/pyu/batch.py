
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
