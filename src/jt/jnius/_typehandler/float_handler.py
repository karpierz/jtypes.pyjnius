# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ...jvm.lib.compat import *
from ...jvm.lib import annotate
from ...jvm.lib import public

from .._constants import EJavaType
from .._constants import EMatchType

from ._base_handler import _PrimitiveHandler
from ._base_handler import num_types


@public
class FloatHandler(_PrimitiveHandler):

    __slots__ = ()

    def __init__(self, state):

        super(FloatHandler, self).__init__(state, EJavaType.FLOAT, "F")

    def match(self, val):

        if isinstance(val, float):
            return EMatchType.PERFECT
        elif isinstance(val, int):
            return EMatchType.IMPLICIT
        return EMatchType.NONE

    def valid(self, val):

        if isinstance(val, num_types):
            min_val, max_val = self._jt_jvm.JObject.minmaxFloatValue()
            if ((val > 0.0 and not ( min_val <= val <=  max_val)) or
                (val < 0.0 and not (-max_val <= val <= -min_val))):
                return False
        return True

    def toJava(self, val):

        return self._jt_jvm.JObject.newFloat(val)

    def toPython(self, val):

        if isinstance(val, self._jt_jvm.JObject):
            return val.floatValue()
        else:
            return val

    def getStatic(self, fld, cls):

        return fld.getStaticFloat(cls)

    def setStatic(self, fld, cls, val):

        raise NotImplementedError("set not implemented for static fields")
        #fld.setStaticFloat(cls, float(val))

    def getInstance(self, fld, this):

        return fld.getFloat(this)

    def setInstance(self, fld, this, val):

        fld.setFloat(this, float(val))

    def setArgument(self, pdescr, args, pos, val):

        args.setFloat(pos, float(val))

    def callStatic(self, meth, cls, args):

        return meth.callStaticFloat(cls, args)

    def callInstance(self, meth, this, args):

        return meth.callInstanceFloat(this, args)

    def newArray(self, size):

        return self._jt_jvm.JArray.newFloatArray(size)

    def getElement(self, arr, idx):

        return arr.getFloat(idx)

    def setElement(self, arr, idx, val):

        arr.setFloat(idx, float(val))

    def getSlice(self, arr, start, stop, step):

        return arr.getFloatSlice(start, stop, step)

    def setSlice(self, arr, start, stop, step, val):

        arr.setFloatSlice(start, stop, step, val)

    def getArrayBuffer(self, arr):

        return arr.getFloatBuffer()

    def releaseArrayBuffer(self, arr, buf):

        arr.releaseFloatBuffer(buf)
