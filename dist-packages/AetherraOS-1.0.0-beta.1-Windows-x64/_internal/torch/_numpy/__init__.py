# mypy: ignore-errors

from math import e, pi  # usort: skip

from . import fft, linalg, random
from ._dtypes import *  # noqa: F403
from ._funcs import *  # noqa: F403
from ._getlimits import finfo, iinfo
from ._ndarray import (
    array,
    asarray,
    ascontiguousarray,
    can_cast,
    from_dlpack,
    ndarray,
    newaxis,
    result_type,
)
from ._ufuncs import *  # noqa: F403
from ._util import AxisError, UFuncTypeError

all = all
alltrue = all

any = any
sometrue = any

inf = float("inf")
nan = float("nan")

False_ = False
True_ = True
