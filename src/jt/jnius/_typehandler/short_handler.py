# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ...jvm.lib.compat import *
from ...jvm.lib import annotate
from ...jvm.lib import public

from .._constants import EJavaType
from .._constants import EMatchType

from ._base_handler import _PrimitiveHandler
from ._base_handler import int_types


@public
class ShortHandler(_PrimitiveHandler):

    __slots__ = ()

    def __init__(self, state):

        super(ShortHandler, self).__init__(state, EJavaType.SHORT, "S")

    def match(self, val):

        if isinstance(val, int) or (isinstance(val, long) and val <= 2147483647):
            return EMatchType.PERFECT
        elif isinstance(val, float):
            return EMatchType.IMPLICIT
        return EMatchType.NONE

    def valid(self, val):

        if isinstance(val, int_types):
            min_val, max_val = self._jt_jvm.JObject.minmaxShortValue()
            if not (min_val <= val <= max_val):
                return False
        return True

    def toJava(self, val):

        return self._jt_jvm.JObject.newShort(val)

    def toPython(self, val):

        if isinstance(val, self._jt_jvm.JObject):
            return val.shortValue()
        else:
            return val

    def getStatic(self, fld, cls):

        return fld.getStaticShort(cls)

    def setStatic(self, fld, cls, val):

        raise NotImplementedError("set not implemented for static fields")
        #fld.setStaticShort(cls, int(val))

    def getInstance(self, fld, this):

        return fld.getShort(this)

    def setInstance(self, fld, this, val):

        fld.setShort(this, int(val))

    def setArgument(self, pdescr, args, pos, val):

        args.setShort(pos, int(val))

    def callStatic(self, meth, cls, args):

        return meth.callStaticShort(cls, args)

    def callInstance(self, meth, this, args):

        return meth.callInstanceShort(this, args)

    def newArray(self, size):

        return self._jt_jvm.JArray.newShortArray(size)

    def getElement(self, arr, idx):

        return arr.getShort(idx)

    def setElement(self, arr, idx, val):

        arr.setShort(idx, int(val))

    def getSlice(self, arr, start, stop, step):

        return arr.getShortSlice(start, stop, step)

    def setSlice(self, arr, start, stop, step, val):

        arr.setShortSlice(start, stop, step, val)

    def getArrayBuffer(self, arr):

        return arr.getShortBuffer()

    def releaseArrayBuffer(self, arr, buf):

        arr.releaseShortBuffer(buf)
