from .iterators import *


def identity(x):
    return x

def pointwise(*fs):
    def _fn(xs):
        return [f(x) for f, x in zip(fs, xs)]
    return _fn

# (b -> a -> b) -> b -> [a] -> b
def foldl(f, init, arr):
    curr = init
    for elem in arr:
        curr = f(curr, elem)
    return curr

# (a -> b -> b) -> b -> [a] -> b
def foldr(f, init, arr):
    curr = init
    for elem in arr[::-1]:
        curr = f(elem, curr)
    return curr

def mean(x):
    return sum(x) / len(x)

class pipeline:
    def __init__(self, *fs):
        self.fs = list(fs)

    def __rrshift__(self, other):
        if isinstance(other, pipeline):
            return pipeline(*(other.fs + self.fs))
        else:
            return self(other)
    
    def __call__(self, x):
        for f in self.fs: x = f(x)

        return x

class each(pipeline):
    def __init__(self, *f):
        self.fs = [lambda xs: (pipeline(*f)(x) for x in xs)]

class join(pipeline):
    def __init__(self):
        self.fs = [self._join]

    def _join(self, xs):
        for it in xs:
            for elem in it:
                yield elem

class filt(pipeline):
    def __init__(self, f):
        self.fs = [self._filter]
        self.f = f

    def _filter(self, xs):
        for elem in xs:
            if self.f(elem):
                yield elem
# aliases
do = pipeline

builtin_filter = filter
def filter(*x):
    if len(x) == 1: return filt(*x)
    if len(x) == 2: return builtin_filter(*x)
    assert False