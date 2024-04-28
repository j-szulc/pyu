import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

class HasShapeMeta(type):

    def __instancecheck__(self, instance):
        print('instance:', instance, "cls", self)
        return hasattr(instance, 'shape')

class HasShape(metaclass=HasShapeMeta):
    pass

class Test:

    def __init__(self):
        self.shape = 1

print(isinstance(Test(), HasShape))