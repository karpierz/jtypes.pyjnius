# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ...jvm.lib.compat import *
from ...jvm.lib import annotate
from ...jvm.lib import public
from ...jvm.lib import issubtype

from .._constants import EJavaType
from .._constants import EMatchType

from ._base_handler import _ObjectHandler


@public
class ClassHandler(_ObjectHandler):

    __slots__ = ()

    def __init__(self, state):

        super(ClassHandler, self).__init__(state, EJavaType.CLASS, "Ljava/lang/Class;")

    def match(self, val):

        if val is None:
            return EMatchType.IMPLICIT
        elif issubtype(val, self._state.class_importer.java_lang_Object):
            return EMatchType.PERFECT
        return EMatchType.NONE

    def valid(self, val):

        return True

    def toJava(self, val):

        if val is None:
            return None
        elif issubtype(val, self._state.class_importer.java_lang_Object):
            return val.__javaclass__.asObject()
        raise TypeError("Cannot convert value to Java class")

    def toPython(self, val):

        if val is None:
            return None
        elif isinstance(val, self._jt_jvm.JClass):
            return self._state.class_importer.defineClass(val)
        elif isinstance(val, self._jt_jvm.JObject):
            return self._state.class_importer.defineClass(val.asClass())
        # what else could it be ...
        raise TypeError("Requires jvm.JClass or jvm.JObject, not {}".format(type(val)))
