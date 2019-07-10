# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ...jvm.lib.compat import *
from ...jvm.lib import annotate
from ...jvm.lib import public

from ...jvm.jtypehandlerabc import TypeHandlerABC

from .._jvm import JVM

int_types  = (int, long)
num_types  = (float, int, long)
str_types  = (builtins.str, str)
byte_types = (bytes, bytearray)


class _BaseHandler(TypeHandlerABC):

    __slots__ = ()

    _jt_jvm = property(lambda self: JVM.jvm)

    def isSubtypeOf(self, other):

        raise NotImplementedError()


class _PrimitiveHandler(_BaseHandler):

    __slots__ = ()

    def valid(self, val):

        return True


class _ObjectHandler(_BaseHandler):

    __slots__ = ()

    def valid(self, val):

        return True

    def getStatic(self, fld, cls):

        jobject = fld.getStaticObject(cls)
        return self.toPython(jobject)

    def setStatic(self, fld, cls, val):

        raise NotImplementedError("set not implemented for static fields")
        #fld.setStaticObject(cls, self.toJava(val))

    def getInstance(self, fld, this):

        jobject = fld.getObject(this)
        return self.toPython(jobject)

    def setInstance(self, fld, this, val):

        fld.setObject(this, self.toJava(val))

    def setArgument(self, pdescr, args, pos, val):

        args.setObject(pos, self.toJava(val))

    def callStatic(self, meth, cls, args):

        jobject = meth.callStaticObject(cls, args)
        return self.toPython(jobject)

    def callInstance(self, meth, this, args):

        jobject = meth.callInstanceObject(this, args)
        return self.toPython(jobject)

    def newArray(self, size):

        return self._jt_jvm.JArray.newObjectArray(size, self._jclass)

    def getElement(self, arr, idx):

        jobject = arr.getObject(idx)
        return self.toPython(jobject)

    def setElement(self, arr, idx, val):

        arr.setObject(idx, self.toJava(val))

    def getSlice(self, arr, start, stop, step):

        return arr.getObjectSlice(start, stop, step)

    def setSlice(self, arr, start, stop, step, val):

        val = [self.toJava(val[ix])
               for ix, _ in enumerate(range(start, stop, step))]
        arr.setObjectSlice(start, stop, step, val)

    def getArrayBuffer(self, arr):

        raise NotImplementedError()

    def releaseArrayBuffer(self, arr, buf):

        raise NotImplementedError()
