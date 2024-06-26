
def system(cmd, *args, __shell=True, __check=True, __capture_output=True, **kwargs):
    # TODO better sanity checks
    import shlex
    import logging
    executable = shlex.split(cmd)[0]
    args = [shlex.quote(str(a)) for a in args]
    kwargs = {k: shlex.quote(str(v)) for k, v in kwargs.items()}
    if args:
        try:
            cmd.format(*args[:-1], **kwargs)
            logging.warning("Arguments were not used in the command string!")
        except IndexError:
            pass
    if kwargs:
        for k in kwargs:
            if "{" + k + "}" not in cmd:
                logging.warning(f"Keyword argument {k} was not used in the command string!")
    cmd = cmd.format(*args, **kwargs)
    if not __shell:
        cmd = shlex.split(cmd)
        # Assert that the argument expansion did not change the executable
        assert cmd[0] == executable, f"Executable mismatch: {cmd[0]} != {executable}"
    logging.debug(f"Running: {cmd}")
    def log(severity, output):
        for line in output.decode(errors="ignore").splitlines():
            logging.log(severity, line)
    import subprocess
    try:
        result = subprocess.run(cmd, shell=__shell, check=__check, capture_output=__capture_output)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running: {cmd}, process returned with non-zero code: {e.returncode}")
        log(logging.ERROR, e.stdout)
        log(logging.ERROR, e.stderr)
        raise e
    if __capture_output:
        log(logging.DEBUG, result.stdout)
        log(logging.WARN, result.stderr)
    return result