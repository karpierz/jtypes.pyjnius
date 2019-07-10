# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ...jvm.lib.compat import *
from ...jvm.lib import annotate
from ...jvm.lib import public
from ...jvm.lib import issequence

from .._constants import EJavaType
from .._constants import EMatchType

from ._base_handler import _ObjectHandler
from ._base_handler import str_types


@public
class StringHandler(_ObjectHandler):

    __slots__ = ()

    def __init__(self, state):

        super(StringHandler, self).__init__(state, EJavaType.STRING, "Ljava/lang/String;")

    def match(self, val):

        if val is None:
            return EMatchType.IMPLICIT
        elif isinstance(val, str_types):
            return EMatchType.PERFECT
        elif isinstance(val, self._class()):#and val.__javaobject__.getClass() == self._class():
            return EMatchType.PERFECT
        return EMatchType.NONE

    def toJava(self, val):

        if val is None:
            return None
        elif isinstance(val, str):
            return self._jt_jvm.JObject.newString(val)
        elif isinstance(val, str_types):
            # never reached for PY>=3
            return self._jt_jvm.JObject.newString(val.decode())
        elif isinstance(val, self._class()):#and val.__javaobject__.getClass() == self._class():
            return val.__javaobject__
        raise TypeError("Cannot convert value to Java string")

    def toPython(self, val):

        if val is None:
            return None
        else:
            if isinstance(val, self._jt_jvm.JObject):
                val = val.stringValue()
            return val

    def getStatic(self, fld, cls):

        return fld.getStaticString(cls)

    def setStatic(self, fld, cls, val):

        raise NotImplementedError("set not implemented for static fields")

    def getInstance(self, fld, this):

        return fld.getString(this)

    def setInstance(self, fld, this, val):

        if val is None:
            fld.setString(this, None)
        elif isinstance(val, str):
            fld.setString(this, val)
        elif isinstance(val, str_types):
            # never reached for PY>=3
            fld.setString(this, val.decode())
        elif isinstance(val, self._class()):
            fld.setObject(this, val.__javaobject__)
        else:
            raise TypeError("Cannot convert value to Java string")

    def setArgument(self, pdescr, args, pos, val):

        if val is None:
            args.setString(pos, None)
        elif isinstance(val, str):
            args.setString(pos, val)
        elif isinstance(val, str_types):
            # never reached for PY>=3
            args.setString(pos, val.decode())
        elif isinstance(val, self._class()):
            args.setObject(pos, val.__javaobject__)
        else:
            raise TypeError("Cannot convert value to Java string")

    def callStatic(self, meth, cls, args):

        value = meth.callStaticString(cls, args)
        return value

    def callInstance(self, meth, this, args):

        value = meth.callInstanceString(this, args)
        return value

    def newArray(self, size):

        return self._jt_jvm.JArray.newStringArray(size)

    def getElement(self, arr, idx):

        return arr.getString(idx)

    def setElement(self, arr, idx, val):

        if val is None:
            arr.setString(idx, None)
        elif isinstance(val, str):
            arr.setString(idx, val)
        elif isinstance(val, str_types):
            # never reached for PY>=3
            arr.setString(idx, val.decode())
        elif isinstance(val, self._class()):
            arr.setObject(idx, val.__javaobject__)
        else:
            raise TypeError("Cannot convert value to Java string")

    def getSlice(self, arr, start, stop, step):

        return arr.getStringSlice(start, stop, step)

    def setSlice(self, arr, start, stop, step, val):

        #if not issequence(val):
        #    raise RuntimeError("Unable to convert to String array")

        val = [self.toJava(val[ix])
               for ix, _ in enumerate(range(start, stop, step))]
        arr.setObjectSlice(start, stop, step, val)
