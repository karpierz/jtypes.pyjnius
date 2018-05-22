# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import absolute_import

import ctypes as ct

from ..jvm.lib.compat import *
from ..jvm.lib import py2compatible
from ..jvm.lib import annotate
from ..jvm.lib import public


@public
@py2compatible
class ByteArray(object):

    def __new__(cls):

        self = super(ByteArray, cls).__new__(cls)
        self._jarr = None
        self._size = 0
        self._buf  = ct.POINTER(ct.c_ubyte)()
        return self

    @annotate(jarr='jt.jvm.JArray')
    def _set_buffer(self, jarr):

        if self._buf:
            raise Exception("Cannot call _set_buffer() twice.")

        with jarr.jvm as (jvm, jenv):
            self._jarr = jarr.jvm.JArray(jenv, jarr.handle)
        self._size = self._jarr.getLength()
        self._buf  = ct.cast(self._jarr.getByteBuffer().buf, ct.POINTER(ct.c_ubyte))

    def __del__(self):

        if self._buf:
            self._jarr.releaseByteBuffer(self._buf)
        self._jarr = None

    def __len__(self):

        return self._size

    def __getitem__(self, idx):

        if isinstance(idx, slice):
            start, stop, step = idx.indices(len(self))
            return self._buf[start:stop:step]
        else:
            size = len(self)
            if idx < 0: idx += size
            if not (0 <= idx < size):
                raise IndexError("array index out of range")
            return self._buf[idx]

    def __eq__(self, other):

        if self is other:
            return True

        one, two = self.__get_cmp_args(other)
        return NotImplemented if one is NotImplemented else (one == two)

    def __lt__(self, other):

        if self is other:
            return False

        one, two = self.__get_cmp_args(other)
        return NotImplemented if one is NotImplemented else (one < two)

    def __gt__(self, other):

        if self is other:
            return False

        one, two = self.__get_cmp_args(other)
        return NotImplemented if one is NotImplemented else (one > two)

    def __ne__(self, other):

        eq = self.__eq__(other)
        return NotImplemented if eq is NotImplemented else not eq

    def __le__(self, other):

        gt = self.__gt__(other)
        return NotImplemented if gt is NotImplemented else not gt

    def __ge__(self, other):

        lt = self.__lt__(other)
        return NotImplemented if lt is NotImplemented else not lt

    def __get_cmp_args(self, other):

        if isinstance(other, (list, tuple)):
            return self.tolist(), other
        elif isinstance(other, ByteArray):
            return self.tostring(), other.tostring()
        else:
            return NotImplemented, NotImplemented

    def __str__(self):

        return u"<ByteArray size={} at {:#x}>".format(len(self), id(self))

    def tolist(self):

        return self._buf[:len(self)]

    def tostring(self):

        return bytes(bytearray(self.tolist()))
