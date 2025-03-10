from pyu.batch import *
from pyu.cli_to_lib import rerun_module
from pyu.traceback import print_traceback
import test2

if __name__ == '__main__':
    try:
        rerun_module(test2, foo="test.py", bar="hello")
    except Exception as e:
        print_traceback(e)