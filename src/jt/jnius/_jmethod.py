# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import absolute_import

from itertools import count

from ..jvm.lib.compat import *
from ..jvm.lib import annotate, Optional
from ..jvm.lib import public
from ..jvm.lib import cached
from ..        import jni

from ._constants import EMatchType
from ._jclass    import JavaException
from ._jvm       import JVM


@public
class JavaMultipleMethod(object):

    # Equivalent of: jt.jtypes.JavaMethod

    #cdef LocalRef j_self
    #cdef bytes name

    def __new__(cls, definitions, **kwargs):

        self = super(JavaMultipleMethod, cls).__new__(cls)
        self.__definitions        = definitions  # list
        self.j_self               = None
        self.name                 = None
        self.__static_overloads   = {}  # JavaStaticMethod
        self.__instance_overloads = {}  # JavaMethod
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
            jc = this  # JavaClass
            self.j_self = jc.j_self
        return self

    def __call__(self, *args):

        # try to match our args to a signature

        best_ovr, _ = self.__match_overload(self.__instance_overloads
                                            if self.j_self else
                                            self.__static_overloads,
                                            *args)
        if best_ovr is None:
            raise JavaException("No methods matching your arguments")

        best_ovr.j_self = self.j_self
        return best_ovr(*args)

    def __match_overload(self, overloads, *args):

        scores = []
        for signature, ovr in overloads.items():
            score = ovr._match_args(args)
            if score > 0:
                scores.append((score, signature))
        scores.sort()

        if not scores:
            return None, EMatchType.NONE

        best_score, signature = scores[-1]
        best_ovr = overloads[signature]

        return best_ovr, best_score


class JavaConstructor(object):

    """Used to resolve a Java constructor, and do the call"""

    # Equivalent of: jt.jtypes.JavaMethodOverload

    def __new__(cls, definition, **kwargs):

        from ._util import parse_definition

        self = super(JavaConstructor, cls).__new__(cls)
        self.is_static  = True
        self.is_varargs = kwargs.get("varargs", False)
        self._definition = definition
        _, self._definition_args = parse_definition(self._definition)
        self.__jclass   = None  # jt.jvm.JClass
        self.name       = "<init>"
        return self

    jcls = property(lambda self: self.__jclass.handle
                    if self.__jclass is not None else jni.obj(jni.jclass))

    @annotate(jclass='jt.jvm.JClass')
    def _set_resolve_info(self, jclass):

        self.__jclass = jclass

    def _match_args(self, args):

        jvm = JVM.jvm

        arg_count  = len(args)
        par_descrs = self._definition_args
        par_count  = len(par_descrs)
        is_varargs = False
        perm_count = (par_count - 1) if is_varargs else par_count

        if arg_count != perm_count:
            # if the number of arguments expected is not the same as the number of arguments
            # the method gets it cannot be the method we are looking for except if the method
            # has varargs aka. it takes an undefined number of arguments
            return EMatchType.NONE

        # if the method has the good number of arguments and doesn't take varargs
        # increment the score so that it takes precedence over a method with the same
        # signature and varargs e.g.:
        # (Integer, Integer)          takes precedence over (Integer, Integer, Integer...)
        # (Integer, Integer, Integer) takes precedence over (Integer, Integer, Integer...)

        score = EMatchType.PERFECT
        for pos, arg_definition, arg in zip(count(), par_descrs, args):
            thandler = jvm.type_manager.get_handler(arg_definition)
            match_level = thandler.match(arg)
            if match_level == EMatchType.NONE:
                return EMatchType.NONE
            score += match_level

        return score

    def __call__(self, *args):

        jvm  = JVM.jvm
        jenv = JVM.jenv

        # get the java constructor
        constructorID = jenv.GetMethodID(self.__jclass.handle,
                                         b"<init>", self._definition.encode("utf-8"))
        jargs = self.__make_arguments(args)
        try:
            from ..jvm.jframe import JFrame
            with JFrame(jenv, 1):
                # create the object
                jobj  = jenv.NewObject(self.__jclass.handle, constructorID, jargs.arguments)
                jself = jvm.JObject(jenv, jobj) if jobj else None
            self.__close_arguments(jargs, args)
        except jni.Throwable as exc:
            raise JavaException.__exception__(jvm.JException(exc))
        return jself

    def __make_arguments(self, args):

        from .__config__ import config

        jvm = JVM.jvm

        par_descrs = self._definition_args
        par_count  = len(par_descrs)
        is_varargs = self.is_varargs
        perm_count = (par_count - 1) if is_varargs else par_count

        if is_varargs:
            args = args[:perm_count] + (args[perm_count:],)

        jargs = jvm.JArguments(par_count)
        if args:
            for pos, arg_definition in enumerate(par_descrs):
                arg = args[pos]
                thandler = jvm.type_manager.get_handler(arg_definition)
                if config.getboolean("WITH_VALID", False) and not thandler.valid(arg):
                    raise ValueError("Parameter value is not valid for required parameter type.")
                thandler.setArgument(arg_definition, jargs, pos, arg)

        return jargs

    def __close_arguments(self, jargs, args):

        from ._conversion import convert_jarray_to_python

        par_descrs = self._definition_args
        par_count  = len(par_descrs)
        is_varargs = self.is_varargs
        perm_count = (par_count - 1) if is_varargs else par_count

        if is_varargs:
            args = args[:perm_count] + (args[perm_count:],)

        for pos, arg_definition in enumerate(par_descrs):
            arg  = args[pos]
            jarg = jargs.arguments[pos]
            is_array = (arg_definition[0] == "[")
            if is_array:
                continue #!!!
                elem_definition = arg_definition[1:]
                jarr = jargs.jvm.JArray(None, jarg.l, borrowed=True) if jarg.l else None
                result = convert_jarray_to_python(elem_definition, jarr)
                try:
                    arg[:] = result
                except TypeError:
                    pass


@public
class JavaMethod(object):

    """Used to resolve a Java method, and do the call"""

    # Equivalent of: jt.jtypes.JavaMethodOverload

    #cdef LocalRef j_self
    #cdef name
    #cdef object is_static
    #cdef bint is_varargs

    def __new__(cls, definition, **kwargs):

        from ._util import parse_definition

        self = super(JavaMethod, cls).__new__(cls)
        self.is_static  = kwargs.get("static",  False)
        self.is_varargs = kwargs.get("varargs", False)
        self.__definition = definition
        self.__definition_return, self.__definition_args = parse_definition(self.__definition)
        self.__jclass   = None  # jt.jvm.JClass
        self.j_self     = None
        self.name       = None
        self.__thandler = None
        return self

    jcls = property(lambda self: self.__jclass.handle
                    if self.__jclass is not None else jni.obj(jni.jclass))

    @annotate(jclass='jt.jvm.JClass', this=Optional['JObjectBase'], name=bytes)
    def _set_resolve_info(self, jclass, this, name):

        self.__jclass   = jclass
        self.j_self     = this
        self.name       = name
        self.__thandler = self.__jclass.jvm.type_manager.get_handler(self.__definition_return)

    def _match_args(self, args):

        arg_count  = len(args)
        par_descrs = self.__definition_args
        par_count  = len(par_descrs)
        is_varargs = self.is_varargs
        perm_count = (par_count - 1) if is_varargs else par_count

        if is_varargs:
            args = args[:perm_count] + (args[perm_count:],)
        else:
            if arg_count != perm_count:
                return EMatchType.NONE

        # if the method has the good number of arguments and doesn't take varargs
        # increment the score so that it takes precedence over a method with the same
        # signature and varargs e.g.:
        # (Integer, Integer)          takes precedence over (Integer, Integer, Integer...)
        # (Integer, Integer, Integer) takes precedence over (Integer, Integer, Integer...)

        score = 0 if is_varargs else EMatchType.PERFECT
        for pos, arg_definition, arg in zip(count(), par_descrs, args):
            thandler = self.__jclass.jvm.type_manager.get_handler(arg_definition)
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
            jc = this  # JavaClass
            self.j_self = jc.j_self
        return self

    def __call__(self, *args):

        arg_count  = len(args)
        par_count  = len(self.__definition_args)
        is_varargs = self.is_varargs
        perm_count = (par_count - 1) if is_varargs else par_count

        if (arg_count < perm_count) if is_varargs else (arg_count != perm_count):
            raise JavaException("Invalid call, number of argument mismatch")

        if self.is_static:
            return self.__call_static(*args)
        else:
            return self.__call_instance(self.j_self, *args)

    def __call_static(self, *args):

        jclass = self.__jclass
        jmeth  = self.__jmethod()
        jargs  = self.__make_arguments(args)
        result = self.__thandler.callStatic(jmeth, jclass, jargs)
        self.__close_arguments(jargs, args)
        return result

    def __call_instance(self, this, *args):

        if not JVM.jenv:
            raise JavaException("Cannot call instance method on a un-instantiated class")
        jmeth  = self.__jmethod()
        jargs  = self.__make_arguments(args)
        result = self.__thandler.callInstance(jmeth, this, jargs)
        self.__close_arguments(jargs, args)
        return result

    @annotate('jt.jvm.JMethod')
    def __jmethod(self):

        if self.name is None:
            raise JavaException("Unable to find a None method!")

        jvm = self.__jclass.jvm if self.is_static else JVM.jvm

        name       = self.name
        is_static  = self.is_static
        jclass     = self.__jclass
        definition = self.__definition

        class JMethod(jvm.JMethod):
            @cached
            def _jmid(self, jenv,
                      name=name, is_static=is_static, jclass=jclass, definition=definition):
                try:
                    GetMethodID = jenv.GetStaticMethodID if is_static else jenv.GetMethodID
                    return GetMethodID(jclass.handle, name.encode("utf-8"), definition.encode("utf-8"))
                except:
                    raise JavaException("Unable to find the method {}({})".format(name, definition))

        return JMethod(None, 1, borrowed=True)  # 1 - trick to avoid exception

    def __make_arguments(self, args):

        from .__config__ import config

        jvm = self.__jclass.jvm if self.is_static else JVM.jvm

        par_descrs = self.__definition_args
        par_count  = len(par_descrs)
        is_varargs = self.is_varargs
        perm_count = (par_count - 1) if is_varargs else par_count

        if is_varargs:
            args = args[:perm_count] + (args[perm_count:],)

        jargs = jvm.JArguments(par_count)
        for pos, arg_definition, arg in zip(count(), par_descrs, args):
            thandler = jvm.type_manager.get_handler(arg_definition)
            if config.getboolean("WITH_VALID", False) and not thandler.valid(arg):
                raise ValueError("Parameter value is not valid for required parameter type.")
            thandler.setArgument(arg_definition, jargs, pos, arg)

        return jargs

    def __close_arguments(self, jargs, args):

        from ._conversion import convert_jarray_to_python

        par_descrs = self.__definition_args
        par_count  = len(par_descrs)
        is_varargs = self.is_varargs
        perm_count = (par_count - 1) if is_varargs else par_count

        if is_varargs:
            args = args[:perm_count] + (args[perm_count:],)

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

    def __new__(cls, definition, **kwargs):

        self = super(JavaStaticMethod, cls).__new__(cls, definition, **kwargs)
        self.is_static = True
        return self
