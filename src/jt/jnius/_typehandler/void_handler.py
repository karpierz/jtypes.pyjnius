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
class VoidHandler(_PrimitiveHandler):

    __slots__ = ()

    def __init__(self, state):

        super(VoidHandler, self).__init__(state, EJavaType.VOID, "V")

    def match(self, val):

        return EMatchType.NONE

    def valid(self, val):

        return True

    def toJava(self, val):

        return None

    def toPython(self, val):

        return None

    def getStatic(self, fld, cls):

        raise RuntimeError("void cannot be the type of a static field.")

    def setStatic(self, fld, cls, val):

        raise RuntimeError("void cannot be the type of a static field.")

    def getInstance(self, fld, this):

        raise RuntimeError("void cannot be the type of a field.")

    def setInstance(self, fld, this, val):

        raise RuntimeError("void cannot be the type of a field.")

    def setArgument(self, pdescr, args, pos, val):

        raise RuntimeError("void cannot be the type of an arument.")

    def callStatic(self, meth, cls, args):

        return meth.callStaticVoid(cls, args)

    def callInstance(self, meth, this, args):

        return meth.callInstanceVoid(this, args)

    def newArray(self, size):

        raise RuntimeError("void cannot be the type of an array.")

    def getElement(self, arr, idx):

        raise RuntimeError("void cannot be the type of an array.")

    def setElement(self, arr, idx, val):

        raise RuntimeError("void cannot be the type of an array.")

    def getSlice(self, arr, start, stop, step):

        raise RuntimeError("void cannot be the type of an array.")

    def setSlice(self, arr, start, stop, step, val):

        raise RuntimeError("void cannot be the type of an array.")

    def getArrayBuffer(self, arr):

        raise RuntimeError("void cannot be the type of an array.")

    def releaseArrayBuffer(self, arr, buf):

        raise RuntimeError("void cannot be the type of an array.")
