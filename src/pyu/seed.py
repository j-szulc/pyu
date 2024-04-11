from abc import ABC, abstractmethod

class Seeder(ABC):

    @abstractmethod
    def set_seed(seed):
        raise NotImplementedError

    @abstractmethod
    def set_state(state_bak):
        raise NotImplementedError

    @abstractmethod
    def get_state():
        raise NotImplementedError

class NumpySeeder(Seeder):

    @staticmethod
    def set_state(state):
        import numpy as np
        np.random.set_state(state)

    @staticmethod
    def set_seed(seed):
        import numpy as np
        NUMPY_RNG_NAME = "MT19937"
        NUMPY_RNG_STATE_SIZE = 624
        arr = np.random.default_rng(seed).random(NUMPY_RNG_STATE_SIZE)
        NumpySeeder.set_state((NUMPY_RNG_NAME,arr, NUMPY_RNG_STATE_SIZE-1,0,0.0))

    @staticmethod
    def get_state():
        import numpy as np
        return np.random.get_state()
    
class TorchSeeder(Seeder):

    @staticmethod
    def set_seed(seed):
        import torch
        torch.manual_seed(seed)
    
    @abstractmethod
    def set_state(state_bak):
        import torch
        torch.set_rng_state(state_bak)

    @staticmethod
    def get_state():
        import torch
        return torch.get_rng_state()

class RandomSeeder(Seeder):

    @staticmethod
    def set_seed(seed):
        import random
        random.seed(seed)

    @staticmethod
    def get_state():
        import random
        return random.getstate()

    @staticmethod
    def set_state(state):
        import random
        random.setstate(state)

class SklearnSeeder(Seeder):
    
    @staticmethod
    def set_seed(seed):
        import sklearn
        sklearn.random.seed(seed)

    @staticmethod
    def get_state():
        import sklearn
        return sklearn.random.getstate()

    @staticmethod
    def set_state(state):
        import sklearn
        sklearn.random.setstate(state)

seeders = {
    'numpy': NumpySeeder,
    'torch': TorchSeeder,
    'random': RandomSeeder,
    'sklearn': SklearnSeeder
}

class Reproducible:

    def __init__(self, seed=None):
        self.seed = seed

    def __enter__(self):
        self.state_baks = {}
        for seeder_libname, seeder_class in seeders.items():
            try:
                self.state_baks[seeder_libname] = seeder_class.get_state()
                if self.seed != None:
                    seeder_class.set_seed(self.seed)
            except ImportError:
                pass
        return self

    def dump_state_baks(self):
        return self.state_baks

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.seed == None:
            return
        for name, state_bak in self.state_baks.items():
            seeders[name].set_state(state_bak)