
class __AbandonDispatch:

    def __str__(self) -> str:
        return "AbandonDispatch"

    def __repr__(self) -> str:
        return "AbandonDispatch"

AbandonDispatch = __AbandonDispatch()

class SuperDispatchMethod:

    def __init__(self, fallback=None):
        self.registry = []
        self.priorities = set()
        def no_fallback(*_, **__):
            raise NotImplementedError("No matching function found and no fallback provided!")
        self.fallback = fallback or no_fallback

    def __sort(self):
        self.registry.sort(key=lambda x: -x[0])

    def is_empty(self):
        return not self.registry

    def register_cond_(self, cond, func, priority=None):
        if priority is None:
            if self.is_empty():
                priority = 0
            else:
                priority = float("inf")
        if priority == float("inf"):
            assert not self.is_empty(), "Cannot register with priority inf when no other functions are registered"
            priority = self.registry[0][0] + 1
        elif priority == float("-inf"):
            assert not self.is_empty(), "Cannot register with priority -inf when no other functions are registered"
            priority = self.registry[-1][0] - 1
        else:
            assert priority not in self.priorities, f"Priority {priority} already registered"
        self.registry.add((priority, cond, func))
        self.priorities.add(priority)
        self.__sort()
    
    def register_type_(self, type, func, priority=None):
        self.register_cond_(lambda x: isinstance(x, type), func, priority)

    def register_cond(self, cond, priority=None):
        def decorator(func):
            self.register_cond_(cond, func, priority)
            return func
        return decorator
    
    def register_type(self, type, priority=None):
        def decorator(func):
            self.register_type_(type, func, priority)
            return func
        return decorator

    def __call__(self, arg, *args, **kwargs):
        for _, cond, func in self.registry:
            if cond(arg):
                result = func(arg, *args, **kwargs)
                if result is not AbandonDispatch:
                    return result
        return self.fallback(arg, *args, **kwargs)
