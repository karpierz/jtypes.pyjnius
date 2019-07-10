# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import absolute_import

import collections as abcoll

from ...jvm.lib.compat import *
from ...jvm.lib import annotate
from ...jvm.lib import public

from .._constants import EJavaType
from .._constants import EMatchType

from ._base_handler import _PrimitiveHandler
from ._base_handler import str_types


@public
class CharHandler(_PrimitiveHandler):

    __slots__ = ()

    def __init__(self, state):

        super(CharHandler, self).__init__(state, EJavaType.CHAR, "C")

    def match(self, val):

        if isinstance(val, str_types):
            if len(val) == 1:
                return EMatchType.PERFECT
        return EMatchType.NONE

    def valid(self, val):

        if isinstance(val, str_types):
            if len(val) != 1:
                return False
        return True

    def toJava(self, val):

        return self._jt_jvm.JObject.newCharacter(val) #!!! ??? chr(val) !!!

    def toPython(self, val):

        if isinstance(val, self._jt_jvm.JObject):
            return val.charValue()
        else:
            return val

    def getStatic(self, fld, cls):

        return fld.getStaticChar(cls)

    def setStatic(self, fld, cls, val):

        raise NotImplementedError("set not implemented for static fields")
        #fld.setStaticChar(cls, chr(val))

    def getInstance(self, fld, this):

        return fld.getChar(this)

    def setInstance(self, fld, this, val):

        fld.setChar(this, chr(val))

    def setArgument(self, pdescr, args, pos, val):

        if isinstance(val, str):
            args.setChar(pos, val)
        elif isinstance(val, str_types):
            # never reached for PY>=3
            args.setChar(pos, val.decode())
        else:
            args.setChar(pos, str(val))

    def callStatic(self, meth, cls, args):

        return meth.callStaticChar(cls, args)

    def callInstance(self, meth, this, args):

        return meth.callInstanceChar(this, args)

    def newArray(self, size):

        return self._jt_jvm.JArray.newCharArray(size)

    def getElement(self, arr, idx):

        return arr.getChar(idx)

    def setElement(self, arr, idx, val):

        arr.setChar(idx, val)

    def getSlice(self, arr, start, stop, step):

        return arr.getCharSlice(start, stop, step)

    def setSlice(self, arr, start, stop, step, val):

        if not isinstance(val, str_types):                            # IF_OLD
            if not isinstance(val, abcoll.Sequence):                  #
                raise RuntimeError("Unable to convert to Char array") #
                                                                      #
        if not isinstance(val, str_types):                            #
       #if not isinstance(val, str): !!!                              #
            val = [self.toJava(val[ix]).charValue()                   #
                   for ix, _ in enumerate(range(start, stop, step))]  #

        arr.setCharSlice(start, stop, step, val)

    def getArrayBuffer(self, arr):

        return arr.getCharBuffer()

    def releaseArrayBuffer(self, arr, buf):

        arr.releaseCharBuffer(buf)
