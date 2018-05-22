# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import absolute_import

from itertools import count

from ..jvm.lib.compat import *
from ..jvm.lib import annotate, Optional
from ..jvm.lib import public
from ..jvm.lib import cached
from ..jvm     import jni

from ._constants import EMatchType
from ._jclass    import JavaException
from ._jvm       import get_jvm


@public
class JavaMultipleMethod(object):

    # Equivalent of: jt.JavaMethod

    #cdef LocalRef j_self
    #cdef bytes name

    def __new__(cls, definitions, **kargs):

        self = super(JavaMultipleMethod, cls).__new__(cls)
        self.__definitions        = definitions  # list
        self.j_self               = None
        self.name                 = None
        self.__static_overloads   = {}
        self.__instance_overloads = {}
        return self

    @annotate(jclass='jt.jvm.JClass', this=Optional['JObjectBase'], name=bytes)
    def _set_resolve_info(self, jclass, this, name):

        self.name = name

        for signature, is_static, is_varargs in self.__definitions:
            if this is None and is_static:
                if signature not in self.__static_overloads:
                    jm = JavaStaticMethod(signature, varargs=is_varargs)
                    jm._set_resolve_info(jclass, None, name)
                    self.__static_overloads[signature] = jm
            elif this is not None and not is_static:
                if signature not in self.__instance_overloads:
                    jm = JavaMethod(signature, varargs=is_varargs)
                    #!!! Here was error ? (jclass, None, name) !!!
                    jm._set_resolve_info(jclass, this, name)
                    self.__instance_overloads[signature] = jm

    def __get__(self, this, cls):

        if this is None:
            self.j_self = None
        else:
            # XXX FIXME we MUST not change our own j_self, but return a "bound"
            # method here, as python does!
            jc = this  # cdef JavaClass jc
            self.j_self = jc.j_self
        return self

    def __call__(self, *args):

        # try to match our args to a signature

        methods = self.__instance_overloads if self.j_self else self.__static_overloads

        scores = []
        for signature, jm in methods.items():
            score = jm._match_args(args)
            if score > 0:
                scores.append((score, signature))

        if not scores:
            raise JavaException("No methods matching your arguments")

        scores.sort()
        score, signature = scores[-1]

        jm = methods[signature]

        jm.j_self = self.j_self
        return jm.__call__(*args)


@public
class JavaMethod(object):

    """Used to resolve a Java method, and do the call"""

    # Equivalent of: jt.JavaMethodOverload

    #cdef LocalRef j_self
    #cdef name
    #cdef object is_static
    #cdef bint is_varargs

    def __new__(cls, definition, **kargs):

        from ._util import parse_definition

        self = super(JavaMethod, cls).__new__(cls)
        self.is_static  = kargs.get("static",  False)
        self.is_varargs = kargs.get("varargs", False)
        self.__definition = definition
        self.__definition_return, self.__definition_args = parse_definition(self.__definition)
        self.__jclass   = None  # jt.jvm.JClass
        self.j_self     = None
        self.name       = None
        self.__thandler = None
        return self

    jcls = property(lambda self: self.__jclass.handle
                                 if self.__jclass is not None else jni.value(jni.jclass))

    @annotate(jclass='jt.jvm.JClass', this=Optional['JObjectBase'], name=bytes)
    def _set_resolve_info(self, jclass, this, name):

        self.__jclass   = jclass
        self.j_self     = this
        self.name       = name
        self.__thandler = self.__jclass.jvm.type_handler.get_handler(self.__definition_return)

    def _match_args(self, args):

        par_count = len(self.__definition_args)

        if not self.is_varargs and len(args) != par_count:
            # if the number of arguments expected is not the same as the number of arguments
            # the method gets it cannot be the method we are looking for except if the method
            # has varargs aka. it takes an undefined number of arguments
            return EMatchType.NONE

        if self.is_varargs: args = args[:par_count - 1] + (args[par_count - 1:],)

        # if the method has the good number of arguments and doesn't take varargs
        # increment the score so that it takes precedence over a method with the same
        # signature and varargs e.g.:
        # (Integer, Integer)          takes precedence over (Integer, Integer, Integer...)
        # (Integer, Integer, Integer) takes precedence over (Integer, Integer, Integer...)

        score = 0 if self.is_varargs else EMatchType.PERFECT
        for pos, arg_definition in enumerate(self.__definition_args):
            arg = args[pos]
            thandler = self.__jclass.jvm.type_handler.get_handler(arg_definition)
            match_level = thandler.match(arg)
            if match_level == EMatchType.NONE:
                return EMatchType.NONE
            score += match_level

        return score

    def __get__(self, this, cls):

        if this is None:
            pass
        else:
            # XXX FIXME we MUST not change our own j_self, but return a "bound"
            # method here, as python does!
            jc = this  # cdef JavaClass jc
            self.j_self = jc.j_self
        return self

    def __call__(self, *args):

        par_count = len(self.__definition_args)

        if self.is_varargs: args = args[:par_count - 1] + (args[par_count - 1:],)

        if len(args) != par_count:
            raise JavaException("Invalid call, number of argument mismatch")

        from ._jvm import get_jenv
        if not self.is_static and not get_jenv():
            raise JavaException("Cannot call instance method on a un-instantiated class")

        if self.name is None:
            raise JavaException("Unable to find a None method!")

        jvm = self.__jclass.jvm if self.is_static else get_jvm()

        name       = self.name
        is_static  = self.is_static
        jclass     = self.__jclass
        definition = self.__definition

        class JMethod(jvm.JMethod):
            @cached
            def _jmid(self, jenv,
                      name=name, is_static=is_static, jclass=jclass, definition=definition):
                try:
                    if is_static:
                        return jenv.GetStaticMethodID(jclass.handle, name.encode("utf-8"), definition.encode("utf-8"))
                    else:
                        return jenv.GetMethodID(jclass.handle, name.encode("utf-8"), definition.encode("utf-8"))
                except:
                    raise JavaException("Unable to find the method {}({})".format(name, definition))

        jmeth = JMethod(None, 1, borrowed=True)  # 1 - trick to avoid exception

        if is_static:
            return self.__call_static(jmeth, self.__jclass, *args)
        else:
            return self.__call_instance(jmeth, self.j_self, *args)

    @annotate(jmeth='jt.jvm.JMethod')
    def __call_static(self, jmeth, jclass, *args):

        jargs  = self.__make_arguments(args)
        result = self.__thandler.callStatic(jmeth, jclass, jargs)
        self.__close_arguments(jargs, args)
        return result

    @annotate(jmeth='jt.jvm.JMethod')
    def __call_instance(self, jmeth, this, *args):

        jargs  = self.__make_arguments(args)
        result = self.__thandler.callInstance(jmeth, this, jargs)
        self.__close_arguments(jargs, args)
        return result

    def __make_arguments(self, args):

        from .__config__ import WITH_VALID

        jvm = self.__jclass.jvm if self.is_static else get_jvm()

        par_descrs = self.__definition_args
        par_count  = len(par_descrs)
        is_varargs = self.is_varargs

        jargs = jvm.JArguments(par_count)
        for pos, arg_definition, arg in zip(count(), par_descrs, args):
            thandler = jvm.type_handler.get_handler(arg_definition)
            if WITH_VALID and not thandler.valid(arg):
                raise ValueError("Parameter value is not valid for required parameter type.")
            thandler.setArgument(arg_definition, jargs, pos, arg)

        return jargs

    def __close_arguments(self, jargs, args):

        from ._conversion import convert_jarray_to_python

        par_descrs = self.__definition_args

        for pos, arg_definition, arg in zip(count(), par_descrs, args):
            jarg = jargs.arguments[pos]
            is_array = (arg_definition[0] == "[")
            if is_array:
                elem_definition = arg_definition[1:]
                jarr = jargs.jvm.JArray(None, jarg.l, borrowed=True) if jarg.l else None
                result = convert_jarray_to_python(elem_definition, jarr)
                try:
                    arg[:] = result
                except TypeError:
                    pass


@public
class JavaStaticMethod(JavaMethod):

    def __new__(cls, definition, **kargs):

        return super(JavaStaticMethod, cls).__new__(cls, definition, static=True, **kargs)
