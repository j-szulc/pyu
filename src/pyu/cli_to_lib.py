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

def backtrack_frame(frame, blacklisted_files):
    while frame.f_code.co_filename in blacklisted_files:
        frame = frame.f_back
    return frame

def backtrack_import(frame):
    return backtrack_frame(frame, ["<frozen importlib._bootstrap_external>", "<frozen importlib._bootstrap>"])

where_imported = backtrack_import(inspect.currentframe().f_back).f_code.co_filename

def rerun_file(file, *args, **kwargs):
    with override_env(
        PYU_CLI_TO_LIB_FORCE_EXCEPTION='0',
        PYU_CLI_TO_LIB_NO_SYSEXIT='1',
        PYU_CLI_TO_LIB_OVERRIDE_ARGS=pyargs_to_cliargs(*args, **kwargs)
    ):
        exec(open(file).read(), {"__name__": "__main__"})

def rerun_where_imported(*args, **kwargs):
    rerun_file(where_imported, *args, **kwargs)

class PatchedArgumentParser(ArgumentParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_file = inspect.currentframe().f_back.f_code.co_filename

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
        if os.getenv('PYU_CLI_TO_LIB_FORCE_EXCEPTION', '0') == '1':
            raise RuntimeError("Forced exception")
        override_args = os.environ.get('PYU_CLI_TO_LIB_OVERRIDE_ARGS')
        if override_args is not None:
            arg_strings.extend(json.loads(override_args))
        return super()._parse_known_args(arg_strings, namespace)

    def rerun_main(self, *args, **kwargs):
        rerun_file(self.main_file, *args, **kwargs)
