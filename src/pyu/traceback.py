
import logging

def custom_tb_frame_string(file, lineno, function, line):
    return f"  File {file}, line {lineno}, in {function}\n    {line}\n"

def custom_tb_string(e, frame_tb_strings):
    return f"Traceback (most recent call last):\n{frame_tb_strings}{e.__class__.__name__}: {e}"

def print_traceback(e, logging_level=None):
    import traceback
    if hasattr(e, "traceback_str"):
        traceback_str = e.traceback_str
    else:
        traceback_str = traceback.format_exc()
    if logging_level is not None:
        for line in traceback_str.split("\n"):
            logging.log(logging_level, line)
    else:
        print(traceback_str)

