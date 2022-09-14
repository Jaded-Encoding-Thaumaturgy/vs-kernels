from __future__ import annotations

from itertools import chain

from . import docs  # noqa: F401
from .abstract import *  # noqa: F401, F403
from .bicubic import *  # noqa: F401, F403
from .fmtconv import *  # noqa: F401, F403
from .impulse import *  # noqa: F401, F403
from .placebo import *  # noqa: F401, F403
from .resize import *  # noqa: F401, F403
from .spline import *  # noqa: F401, F403
from .various import *  # noqa: F401, F403

_modules = ['abstract', 'bicubic', 'fmtconv', 'impulse', 'placebo', 'resize', 'spline', 'various']
__all__ = list(chain.from_iterable(
    __import__(__name__ + '.' + _module, fromlist=_modules).__all__ for _module in _modules
))
