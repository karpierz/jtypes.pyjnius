# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ...jvm.lib.compat import *
from ...jvm.lib import annotate
from ...jvm.lib import public

from .._constants import EJavaType
from .._constants import EMatchType

from ._base_handler import _PrimitiveHandler


@public
class BooleanHandler(_PrimitiveHandler):

    __slots__ = ()

    def __init__(self, state):

        super(BooleanHandler, self).__init__(state, EJavaType.BOOLEAN, "Z")

    def match(self, val):

        if isinstance(val, bool):
            return EMatchType.PERFECT
        return EMatchType.NONE

    def toJava(self, val):

        return self._jt_jvm.JObject.newBoolean(bool(val))

    def toPython(self, val):

        if isinstance(val, self._jt_jvm.JObject):
            return val.booleanValue()
        else:
            return bool(val)

    def getStatic(self, fld, cls):

        return fld.getStaticBoolean(cls)

    def setStatic(self, fld, cls, val):

        raise NotImplementedError("set not implemented for static fields")
        #fld.setStaticBoolean(cls, bool(val))

    def getInstance(self, fld, this):

        return fld.getBoolean(this)

    def setInstance(self, fld, this, val):

        fld.setBoolean(this, bool(val))

    def setArgument(self, pdescr, args, pos, val):

        args.setBoolean(pos, bool(val))

    """
    elif arg_definition == "C":

        args.setChar(pos, val)
    """

    def callStatic(self, meth, cls, args):

        return meth.callStaticBoolean(cls, args)

    def callInstance(self, meth, this, args):

        return meth.callInstanceBoolean(this, args)

    def newArray(self, size):

        return self._jt_jvm.JArray.newBooleanArray(size)

    def getElement(self, arr, idx):

        return arr.getBoolean(idx)

    def setElement(self, arr, idx, val):

        arr.setBoolean(idx, bool(val))

    def getSlice(self, arr, start, stop, step):

        return arr.getBooleanSlice(start, stop, step)

    def setSlice(self, arr, start, stop, step, val):

        arr.setBooleanSlice(start, stop, step, val)

    def getArrayBuffer(self, arr):

        return arr.getBooleanBuffer()

    def releaseArrayBuffer(self, arr, buf):

        arr.releaseBooleanBuffer(buf)
