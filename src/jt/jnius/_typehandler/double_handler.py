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
class DoubleHandler(_PrimitiveHandler):

    __slots__ = ()

    def __init__(self, state):

        super(DoubleHandler, self).__init__(state, EJavaType.DOUBLE, "D")

    def match(self, val):

        if isinstance(val, float):
            return EMatchType.PERFECT
        elif isinstance(val, int):
            return EMatchType.IMPLICIT
        return EMatchType.NONE

    def valid(self, val):

        if isinstance(val, int_types):
            min_val, max_val = self._jt_jvm.JObject.minmaxDoubleValue()
            if ((val > 0.0 and not ( min_val <= val <=  max_val)) or
                (val < 0.0 and not (-max_val <= val <= -min_val))):
                return False
        return True

    def toJava(self, val):

        return self._jt_jvm.JObject.newDouble(val)

    def toPython(self, val):

        if isinstance(val, self._jt_jvm.JObject):
            return val.doubleValue()
        else:
            return val

    def getStatic(self, fld, cls):

        return fld.getStaticDouble(cls)

    def setStatic(self, fld, cls, val):

        raise NotImplementedError("set not implemented for static fields")
        #fld.setStaticDouble(cls, float(val))

    def getInstance(self, fld, this):

        return fld.getDouble(this)

    def setInstance(self, fld, this, val):

        fld.setDouble(this, float(val))

    def setArgument(self, pdescr, args, pos, val):

        args.setDouble(pos, float(val))

    def callStatic(self, meth, cls, args):

        return meth.callStaticDouble(cls, args)

    def callInstance(self, meth, this, args):

        return meth.callInstanceDouble(this, args)

    def newArray(self, size):

        return self._jt_jvm.JArray.newDoubleArray(size)

    def getElement(self, arr, idx):

        return arr.getDouble(idx)

    def setElement(self, arr, idx, val):

        arr.setDouble(idx, float(val))

    def getSlice(self, arr, start, stop, step):

        return arr.getDoubleSlice(start, stop, step)

    def setSlice(self, arr, start, stop, step, val):

        arr.setDoubleSlice(start, stop, step, val)

    def getArrayBuffer(self, arr):

        return arr.getDoubleBuffer()

    def releaseArrayBuffer(self, arr, buf):

        arr.releaseDoubleBuffer(buf)
