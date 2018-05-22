# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ..jvm.lib.compat import *
from ..jvm.lib import annotate
from ..jvm.lib import public
from ..jvm     import jni

from ._jclass import JavaException


@public
class JavaField(object):

    # Equivalent of: jt.JavaField

    def __new__(cls, definition, **kargs):

        self = super(JavaField, cls).__new__(cls)
        self.is_static    = kargs.get("static", False)
        self.__definition = definition
        self.__jclass     = None  # jt.jvm.JClass
        self.__jfield     = None  # jt.jvm.JField
        self.__thandler   = None
        return self

    jcls = property(lambda self: self.__jclass.handle
                                 if self.__jclass is not None else jni.value(jni.jclass))

    @annotate(jclass='jt.jvm.JClass', name=bytes)
    def _set_resolve_info(self, jclass, name):

        self.__jclass = jclass
        try:
            self.__jfield = self.__jclass.getField(name)
        except:
            raise JavaException("Unable to found the field {}".format(name))
        self.__thandler = self.__jfield.jvm.type_handler.get_handler(self.__definition)

    def __get__(self, this, cls):

        if self.__jfield is None:
            raise JavaException("Unable to find a None field!")

        if this is None:
            return self.__thandler.getStatic(self.__jfield, self.__jclass)
        else:
            return self.__thandler.getInstance(self.__jfield, this.j_self)

    def __set__(self, this, value):

        from .__config__ import WITH_VALID

        if self.__jfield is None:
            raise JavaException("Unable to find a None field!")

        if this is None:
            raise NotImplementedError("set not implemented for static fields")

        if self.__definition[0] != "[":

            if WITH_VALID and not self.__thandler.valid(value):
                raise ValueError("Assigned value is not valid for required field type.")

            self.__thandler.setInstance(self.__jfield, this.j_self, value)
        else:
            fld, this, val = self.__jfield, this.j_self, value

            elem_definition = self.__definition[1:]


@public
class JavaStaticField(JavaField):

    def __new__(cls, definition, **kargs):

        return super(JavaStaticField, cls).__new__(cls, definition, static=True, **kargs)
