from .traceback import custom_tb_frame_string, custom_tb_string

def __gen_random_string(length=10):
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def __format_exception(e, discriminator, filename, code):
    import traceback
    frames = [f[0] for f in traceback.walk_tb(e.__traceback__)]
    tb_lines = list(traceback.format_tb(e.__traceback__))
    codelines = code.split("\n")
    for i, frame in enumerate(frames):
        if discriminator in frame.f_globals:
            tb_lines[i] = custom_tb_frame_string(file=filename, lineno=frame.f_lineno, function=frame.f_code.co_name, line=codelines[frame.f_lineno-1])
    tb_str = custom_tb_string(e, "".join(tb_lines))
    return tb_str

def exec_file(file, extra_globals=None):
    if extra_globals is None:
        extra_globals = {}
    discriminator = __gen_random_string()
    with open(file) as f:
        code = f.read()
    try:
        exec(code, {**globals(), "__name__": "__main__", **extra_globals, discriminator: None})
    except Exception as e:
        e.traceback_str = __format_exception(e, discriminator, file, code)
        raise e