import pickle, dill
import inspect

class A:

    def __reduce__(self):
        frame = inspect.currentframe().f_back
        while frame.f_code.co_filename != __file__:
            frame = frame.f_back
        print(f"I've been called in line {frame.f_lineno} in {frame.f_code.co_filename}")
        return (A, tuple())

pickle.dumps(A())
dill.dumps(A())

# Output:
# Hello!
# Hello!

class B:
    
    def __init__(self, x):
        pass
    
dill.dumps(B(A()))

@dill.register(B)
def _pickle_B(pickler, obj):
    print(pickler)
    pickler.save_reduce(B, (A(),))

dill.dumps(B(A()))

# @dill.register(B)
# def _pickle_B(obj):
#     return 