# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ...jvm.lib.compat import *
from ...jvm.lib import annotate
from ...jvm.lib import public
from ...jvm.lib import issequence

from .._constants import EJavaType
from .._constants import EMatchType

from ._base_handler import _PrimitiveHandler
from ._base_handler import int_types, byte_types


@public
class ByteHandler(_PrimitiveHandler):

    __slots__ = ()

    def __init__(self, state):

        super(ByteHandler, self).__init__(state, EJavaType.BYTE, "B")

    def match(self, val):

        if isinstance(val, int):
            return EMatchType.PERFECT
        return EMatchType.NONE

    def valid(self, val):

        if isinstance(val, int_types):
            min_val, max_val = self._jt_jvm.JObject.minmaxByteValue()
            if not (min_val <= val <= max_val):
                return False
        return True

    def toJava(self, val):

        return self._jt_jvm.JObject.newByte(val)

    def toPython(self, val):

        if isinstance(val, self._jt_jvm.JObject):
            return val.byteValue()
        else:
            return val

    def getStatic(self, fld, cls):

        return fld.getStaticByte(cls)

    def setStatic(self, fld, cls, val):

        raise NotImplementedError("set not implemented for static fields")
        #fld.setStaticByte(cls, int(val))

    def getInstance(self, fld, this):

        return fld.getByte(this)

    def setInstance(self, fld, this, val):

        fld.setByte(this, int(val))

    def setArgument(self, pdescr, args, pos, val):

        args.setByte(pos, int(val))

    def callStatic(self, meth, cls, args):

        return meth.callStaticByte(cls, args)

    def callInstance(self, meth, this, args):

        return meth.callInstanceByte(this, args)

    def newArray(self, size):

        return self._jt_jvm.JArray.newByteArray(size)

    def getElement(self, arr, idx):

        return arr.getByte(idx)

    def setElement(self, arr, idx, val):

        arr.setByte(idx, int(val))

    def getSlice(self, arr, start, stop, step):

        return arr.getByteSlice(start, stop, step)

    def setSlice(self, arr, start, stop, step, val):

        if not isinstance(val, byte_types):                           # IF_OLD
            if not issequence(val):                                   #
                raise RuntimeError("Unable to convert to Byte array") #
            val = [self.toJava(val[ix]).byteValue()                   #
                   for ix, _ in enumerate(range(start, stop, step))]  #

        arr.setByteSlice(start, stop, step, val)

    def getArrayBuffer(self, arr):

        return arr.getByteBuffer()

    def releaseArrayBuffer(self, arr, buf):

        arr.releaseByteBuffer(buf)
