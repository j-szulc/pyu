import os
import dill

for i in range(33):
    x = os.urandom(2**i)
    print(f"Size of x: 2^{i} bytes, time: ", end="")
    %timeit dill.dumps(x)