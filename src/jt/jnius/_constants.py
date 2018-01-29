# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ..jvm.lib import public
from ..jvm.lib import enumc

public(
EMatchType = enumc(
    NONE     = -1,
    EXPLICIT =  1,
    IMPLICIT =  5,
    PERFECT  = 10,
))
