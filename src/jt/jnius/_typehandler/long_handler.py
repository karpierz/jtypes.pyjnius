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
class LongHandler(_PrimitiveHandler):

    __slots__ = ()

    def __init__(self, state):

        super(LongHandler, self).__init__(state, EJavaType.LONG, "J")

    def match(self, val):

        if isinstance(val, (int, long)):
            return EMatchType.PERFECT
        elif isinstance(val, float):
            return EMatchType.IMPLICIT
        return EMatchType.NONE

    def valid(self, val):

        if isinstance(val, int_types):
            min_val, max_val = self._jt_jvm.JObject.minmaxLongValue()
            if not (min_val <= val <= max_val):
                return False
        return True

    def toJava(self, val):

        return self._jt_jvm.JObject.newLong(val)

    def toPython(self, val):

        if isinstance(val, self._jt_jvm.JObject):
            return val.longValue()
        else:
            return val

    def getStatic(self, fld, cls):

        return fld.getStaticLong(cls)

    def setStatic(self, fld, cls, val):

        raise NotImplementedError("set not implemented for static fields")
        #fld.setStaticLong(cls, long(val))

    def getInstance(self, fld, this):

        return fld.getLong(this)

    def setInstance(self, fld, this, val):

        fld.setLong(this, long(val))

    def setArgument(self, pdescr, args, pos, val):

        args.setLong(pos, long(val))

    def callStatic(self, meth, cls, args):

        return meth.callStaticLong(cls, args)

    def callInstance(self, meth, this, args):

        return meth.callInstanceLong(this, args)

    def newArray(self, size):

        return self._jt_jvm.JArray.newLongArray(size)

    def getElement(self, arr, idx):

        return arr.getLong(idx)

    def setElement(self, arr, idx, val):

        arr.setLong(idx, long(val))

    def getSlice(self, arr, start, stop, step):

        return arr.getLongSlice(start, stop, step)

    def setSlice(self, arr, start, stop, step, val):

        arr.setLongSlice(start, stop, step, val)

    def getArrayBuffer(self, arr):

        return arr.getLongBuffer()

    def releaseArrayBuffer(self, arr, buf):

        arr.releaseLongBuffer(buf)
