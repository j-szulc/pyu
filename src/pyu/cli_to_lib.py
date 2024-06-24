### Usage:
# Change "argparse.ArgumentParser" to "pyu.cli_to_lib.PatchedArgumentParser" in your code.
# The CLI will work normally, however you have the option to rerun the main function with different arguments.
#
# Example:
## test.py
## from pyu.cli_to_lib import PatchedArgumentParser
## if __name__ == '__main__':
##     parser = PatchedArgumentParser()
##     parser.add_argument('--foo', required=True, type=int)
##     args = parser.parse_args()
##     print(args.foo)
##
# python -i test.py --foo 1
# 1
# >>> parser.rerun_main('--foo', 2)
# 2
#
# You can also force an exception to be raised so that executing main code is only possible through rerun_main.
# Example:
# PYU_CLI_TO_LIB_FORCE_EXCEPTION=1 python -i test.py --foo 1
# ...
# RuntimeError: Forced exception
# >>> parser.rerun_main('--foo', 2)
# 2


from argparse import ArgumentParser, Namespace
import sys
import os
import json
from pyu.env_utils import override_env
from typing import List, Tuple
import inspect

class ForcedException(Exception):
    pass

def pyargs_to_cliargs(*args, **kwargs):
    def generator():
        for arg in args:
            if isinstance(arg, str):
                yield arg
            else:
                raise ValueError(f"Invalid argument {arg}")
        for key, value in kwargs.items():
            if len(key) == 1:
                yield f"-{key}"
            else:
                yield f"--{key}"
            yield str(value)
    return json.dumps(list(generator()))

default_parser = None

def rerun_file(file, *args, **kwargs):
    with override_env(
        PYU_CLI_TO_LIB_NO_SYSEXIT='1',
        PYU_CLI_TO_LIB_OVERRIDE_ARGS=pyargs_to_cliargs(*args, **kwargs)
    ):
        exec(open(file).read(), {**globals(), "__name__": "__main__"})

def reparse_file(file, *args, **kwargs):
    with override_env(
        PYU_CLI_TO_LIB_CAPTURE_ARGS_FLAG='1',
        PYU_CLI_TO_LIB_CAPTURED_ARGS="",
        PYU_CLI_TO_LIB_STORE_DEFAULT_PARSER="1",
        PYU_CLI_TO_LIB_FORCE_EXCEPTION="1",
    ):
        try:
            rerun_file(file, *args, **kwargs)
            raise RuntimeError("Expected ForcedException to be raised!")
        except ForcedException:
            pass
        captured = os.environ.get("PYU_CLI_TO_LIB_CAPTURED_ARGS")
        if captured is None:
            raise ValueError("Failed to capture arguments!")
        arg_strings = json.loads(captured)
    with override_env(
        PYU_CLI_TO_LIB_FORCE_EXCEPTION="0",
    ):
        return default_parser.parse_args(arg_strings)

def get_module_path(m):
    try:
        return m.__path__
    except AttributeError:
        return m.__file__

def rerun_module(m, *args, **kwargs):
    rerun_file(get_module_path(m), *args, **kwargs)

def reparse_module(m, *args, **kwargs):
    with override_env(
        PYU_CLI_TO_LIB_FORCE_MAIN_FILE=get_module_path(m),
    ):
        return reparse_file(get_module_path(m), *args, **kwargs)

class PatchedArgumentParser(ArgumentParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_file = os.environ.get('PYU_CLI_TO_LIB_FORCE_MAIN_FILE')
        if self.main_file is None:
            self.main_file = inspect.currentframe().f_back.f_code.co_filename
        if os.getenv('PYU_CLI_TO_LIB_STORE_DEFAULT_PARSER', '0') == '1':
            global default_parser
            default_parser = self

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.

        If you override this in a subclass, it should not return -- it
        should either exit or raise an exception.
        """
        if os.getenv('PYU_CLI_TO_LIB_NO_SYSEXIT', '0') == '1':
            self.print_usage(sys.stderr)
            args = {'prog': self.prog, 'message': message}
            err_msg = '%(prog)s: error: %(message)s\n' % args
            raise ValueError(err_msg)
        else:
            super().error(message)

    def _parse_known_args(self, arg_strings: List[str], namespace: Namespace) -> Tuple[Namespace, List[str]]:
        force_exception = (os.getenv('PYU_CLI_TO_LIB_FORCE_EXCEPTION', '0') == '1')
        capture_args = (os.getenv('PYU_CLI_TO_LIB_CAPTURE_ARGS_FLAG', '0') == '1')
        override_args = os.environ.get('PYU_CLI_TO_LIB_OVERRIDE_ARGS')

        if force_exception and not capture_args:
            raise ForcedException()
        if override_args is not None:
            # TODO: extend instead of replacing
            arg_strings = json.loads(override_args)
        result = super()._parse_known_args(arg_strings, namespace)
        if capture_args:
            os.environ["PYU_CLI_TO_LIB_CAPTURED_ARGS"] = json.dumps(arg_strings)
        if force_exception:
            raise ForcedException()
        return result

    def rerun_main(self, *args, **kwargs):
        rerun_file(self.main_file, *args, **kwargs)

    def reparse_main(self, *args, **kwargs):
        return reparse_file(self.main_file, *args, **kwargs)
