# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

"""
Pyjnius
=======

Accessing Java classes from Python.

All the documentation is available at: https://pyjnius.readthedocs.io

"""

from . import __config__ ; del __config__
from .__about__ import * ; del __about__

from ._main   import *  # noqa
from .reflect import *  # noqa
