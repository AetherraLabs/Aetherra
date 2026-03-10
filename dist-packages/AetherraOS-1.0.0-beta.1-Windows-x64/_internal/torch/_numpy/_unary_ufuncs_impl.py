# mypy: ignore-errors

"""Export torch work functions for unary ufuncs, rename/tweak to match numpy.
This listing is further exported to public symbols in the `_numpy/_ufuncs.py` module.
"""

import torch
from torch import (  # noqa: F401
    absolute as fabs,
)
from torch import (
    conj_physical as conjugate,
)


# special cases: torch does not export these names
def cbrt(x):
    return torch.pow(x, 1 / 3)


def positive(x):
    return +x


def absolute(x):
    # work around torch.absolute not impl for bools
    if x.dtype == torch.bool:
        return x
    return torch.absolute(x)


# TODO set __name__ and __qualname__
abs = absolute
conj = conjugate
