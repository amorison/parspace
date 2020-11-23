"""Parameter space exploration tool.

See the documentation at https://github.com/amorison/parspace
"""

from itertools import product


class ParSpace:
    """Parameter space explorer.

    Example:
        >>> @ParSpace(asp=[0.5, 1, 2],
        >>>           density=[1, 10])
        >>> def launch_simu(asp, density):
        >>>     print(f"aspect ratio {asp} and density {density}")
        >>> launch_simu()
        aspect ratio 0.5 and density 1
        aspect ratio 0.5 and density 10
        aspect ratio 1 and density 1
        aspect ratio 1 and density 10
        aspect ratio 2 and density 1
        aspect ratio 2 and density 10
    """

    def __init__(self, **space):
        self._space = space
        self._thunk = None

    def _sweeper(self):
        parnames = list(self._space.keys())
        for comb in product(*(self._space[name] for name in parnames)):
            yield dict(zip(parnames, comb))

    def __iter__(self):
        if self._thunk is None:
            yield from self._sweeper()
            return
        for pars in self._sweeper():
            yield pars, self._thunk(**pars)

    def __call__(self, func=None):
        if func is not None:
            self._thunk = func
            return self
        for _ in iter(self):
            pass
