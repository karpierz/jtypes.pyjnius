# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import absolute_import

from itertools import count

from ..jvm.lib.compat import *
from ..jvm.lib import metaclass
from ..jvm.lib import annotate, Optional
from ..jvm.lib import public
from ..        import jni

from ._constants import EMatchType
from ._jproxy    import PythonJavaClass
from ._jvm       import JVM


@public
class java_class(object):

    def __new__(cls, signature=None):

        self = super(java_class, cls).__new__(cls)
        self.signature = signature
        return self

    def __call__(self, klass):

        if self.signature is not None:
            klass.__javaclass__ = self.signature
        return metaclass(MetaJavaClass)(klass)


@public
class MetaJavaBase(type):

    def __instancecheck__(cls, instance):

        jvm  = JVM.jvm
        jenv = JVM.jenv

        meta_jclass = getattr(cls, "_jclass", None)

        jobject = None
        if isinstance(instance, (bytes, str)):
            jobject = jvm.JObject.newString(u"")
        elif isinstance(instance, JavaClass):
            jc = instance  # JavaClass
            jobject = jvm.JObject(jenv, jc.j_self.handle) if jc.j_self.handle else None
        elif isinstance(instance, JavaObject):
            jobject = jvm.JObject(jenv, instance.handle) if instance.handle else None
        elif isinstance(instance, PythonJavaClass):
            # from python class, get the proxy/python class
            if instance.j_self is None: instance._init_j_self_ptr()
            jc = instance.j_self  # JavaClass
            jobject = jvm.JObject(jenv, jc.j_self.handle) if jc.j_self.handle else None

        if jobject:
            if meta_jclass is not None and meta_jclass.isInstance(jobject):
                return True
            try:
                Proxy = jvm.JClass.forName("java.lang.reflect.Proxy")
            except:
                pass
            else:
                if Proxy.isInstance(jobject):
                    # instance is a proxy object. check whether it's one of ours
                    getInvocationHandlerID = jenv.GetStaticMethodID(Proxy.handle,
                                                  b"getInvocationHandler",
                                                  b"(Ljava/lang/Object;)"
                                                  b"Ljava/lang/reflect/InvocationHandler;")
                    jargs = jni.new_array(jni.jvalue, 1)
                    jargs[0].l = jobject.handle
                    ihandler = jenv.CallStaticObjectMethod(Proxy.handle,
                                                           getInvocationHandlerID, jargs)
                    try:
                        ProxyHandler = jvm.JClass.forName("com.jt.reflect.ProxyHandler")
                    except:
                        # ProxyHandler is not reliably in the classpath. don't crash if it's
                        # not there, because it's impossible to get this far with
                        # a PythonJavaClass without it, so we can safely assume this is just
                        # a POJO from elsewhere.
                        pass
                    else:
                        targetID = jenv.GetFieldID(ProxyHandler.handle, b"target", b"J")
                        target = jenv.GetLongField(ihandler, targetID)
                        wrapped_python = jni.from_oid(target)
                        if wrapped_python is not None and wrapped_python is not instance:
                            if isinstance(wrapped_python, cls):
                                return True

        return super(MetaJavaBase, cls).__instancecheck__(instance)


@public
class MetaJavaClass(MetaJavaBase):

    # Equivalent of: jt.jtypes.JavaClass

    _jclass_register = {}

    @staticmethod
    def get_javaclass(name):

        return MetaJavaClass._jclass_register.get(name)

    def __new__(mcls, name, bases, members):

        if not "__javaclass__" in members:
            raise JavaException("__javaclass__ definition missing")

        if not bases or bases == (object,):
            bases = (JavaClass,)
        elif JavaClass not in bases:
            bases = (JavaClass,) + bases
        mcls.__resolve(members)

        self = super(MetaJavaClass, mcls).__new__(mcls, builtins.str(name), bases, members)
        MetaJavaClass._jclass_register[members["__javaclass__"]] = self
        return self

    def __subclasscheck__(cls, subclass):

        jvm = JVM.jvm

        this_jclass = cls._jclass

        if isinstance(subclass, JavaClass):
            other_jclass = subclass.j_self.asClass() if subclass.j_self else None
        else:
            other_jclass = getattr(subclass, "_jclass", None)

        if other_jclass is not None:
            if this_jclass.isAssignableFrom(other_jclass):
                return True
        else:
            for iname in getattr(subclass, "__javainterfaces__", []):
                try:
                    other_jclass = jvm.JClass.forName(iname.replace("/", "."))
                except:
                    pass
                else:
                    if this_jclass.isAssignableFrom(other_jclass):
                        return True

        return super(MetaJavaClass, cls).__subclasscheck__(subclass)

    @classmethod
    def __resolve(mcls, clsdict):

        # search the Java class, and bind to our object

        from ._jfield  import JavaField
        from ._jmethod import JavaMethod, JavaMultipleMethod

        __javaclass__      = clsdict["__javaclass__"]
        __javabaseclass__  = clsdict.get("__javabaseclass__",  "")
        __javainterfaces__ = clsdict.get("__javainterfaces__", "")

        jvm  = JVM.jvm
        jenv = JVM.jenv

        if __javainterfaces__ and __javabaseclass__:

            #!!! Tu sprawdzic (JFrame, jclass itp)

            baseclass  = jvm.JClass.forName(__javabaseclass__.replace("/", "."))
            interfaces = jni.new_array(jni.jclass, len(__javainterfaces__))
            for i, iname in enumerate(__javainterfaces__):
                interfaces[i] = jenv.FindClass(iname.encode("utf-8"))

            getClassLoader = jenv.GetStaticMethodID(baseclass.handle, b"getClassLoader", b"()Ljava/lang/Class;")
            getProxyClass  = jenv.GetStaticMethodID(baseclass.handle, b"getProxyClass",  b"(Ljava/lang/ClassLoader,[Ljava/lang/Class;)Ljava/lang/Class;")

            # with _nogil():
            try:
                cloader = jenv.CallStaticObjectMethod(baseclass.handle, getClassLoader)
                jargs = jni.new_array(jni.jobject, 2)
                jargs[0] = cloader
                jargs[1] = interfaces
                jcls = jenv.CallStaticObjectMethod(baseclass.handle, getProxyClass, jargs)
            except:
                raise JavaException("Unable to create the class {}".format(__javaclass__))
            if not jcls:
                raise JavaException("Unable to create the class {}".format(__javaclass__))

            del baseclass

            jclass = jvm.JClass(jenv, jcls)

            #!!!
        else:
            try:
                jclass = jvm.JClass.forName(__javaclass__.replace("/", "."))
            except:
                raise JavaException("Unable to find the class {}".format(__javaclass__))

        # XXX do we need to grab a ref here?
        # -> Yes, according to http://developer.android.com/training/articles/perf-jni.html
        #    in the section Local and Global References
        clsdict["_jclass"] = jclass

        # resolve all the static JavaField and JavaMethod within our class
        for name, item in clsdict.items():
            if isinstance(item, JavaField):
                if item.is_static:
                    item._set_resolve_info(jclass, name)
            elif isinstance(item, JavaMethod):
                if item.is_static:
                    item._set_resolve_info(jclass, None, name)
            elif isinstance(item, JavaMultipleMethod):
                item._set_resolve_info(jclass, None, name)


@public
class JavaClass(object):

    """Main class to do introspection."""

    # Equivalent of: jt.jtypes.JavaObject

    def __new__(cls, *args, **kwargs):

        self = super(JavaClass, cls).__new__(cls)
        self.j_self = None
        # copy the current attribute in the storage to our class
        if "noinstance" not in kwargs:
            self.j_self = self.__call_constructor(*args)
            self.__resolve()
        return self

    jcls = property(lambda self: self._jclass.handle)

    @annotate(jself=Optional['JObjectBase'])
    def _instantiate_from(self, jself, own=True):

        self.j_self = jself.jvm.JObject.fromObject(jself) if own else jself
        self.__resolve()

    def __resolve(self):

        # resolve all the non static JavaField and JavaMethod within our class

        from ._jfield  import JavaField
        from ._jmethod import JavaMethod, JavaMultipleMethod

        for name, item in self.__class__.__dict__.items():
            if isinstance(item, JavaField):
                if not item.is_static:
                    item._set_resolve_info(self._jclass, name)
            elif isinstance(item, JavaMethod):
                if not item.is_static:
                    item._set_resolve_info(self._jclass, self.j_self, name)
            elif isinstance(item, JavaMultipleMethod):
                item._set_resolve_info(self._jclass, self.j_self, name)

    def __call_constructor(self, *args):

        # find the class constructor and call it with the correct arguments.

        # get the constructor definition if exist
        definitions = getattr(self, "__javaconstructor__", [("()V", False)])
        if isinstance(definitions, (bytes, str)):
            definitions = [definitions]

        if len(definitions) == 0:
            raise JavaException("No constructor available")

        best_ovr, _ = self.__match_overload(definitions, *args)
        best_ovr._set_resolve_info(self._jclass)

        try:
            JVM.jenv.GetMethodID(self._jclass.handle,
                                 b"<init>", best_ovr._definition.encode("utf-8"))
        except:
            raise JavaException("Unable to found the constructor for {}".format(self.__javaclass__))
        jself = best_ovr(*args)
        if not jself:
            raise JavaException("Unable to instantiate {}".format(self.__javaclass__))
        return jself

    def __match_overload(self, definitions, *args):

        from ._jmethod import JavaConstructor

        is_single_constructor = (len(definitions) == 1)

        scores = []
        for signature, is_varargs in definitions:
            ovr = JavaConstructor(signature, varargs=is_varargs)

            if is_single_constructor:
                if len(args) != len(ovr._definition_args or ()):
                    raise JavaException("Invalid call, number of argument mismatch for "
                                        "constructor, available: {}".format([signature]))

            score = 0 if is_single_constructor else ovr._match_args(*args)
            if score != EMatchType.NONE:
                scores.append((score, signature, ovr))
        scores.sort()

        if not scores:
            raise JavaException("No constructor matching your arguments, available: "
                                "{}".format([signature for signature, _ in definitions]))

        best_score, signature, best_ovr = scores[-1]
        return best_ovr, best_score

    def __repr__(self):

        return "<{} at {:#x} jclass={} jself={}>".format(self.__class__.__name__, id(self),
                                                         self.__javaclass__, self.j_self)


@public
class JavaObject(object):

    """Can contain any Java object. Used to store instance, or whatever."""

    def __new__(cls):

        self = super(JavaObject, cls).__new__(cls)
        self.obj = jni.NULL
        return self

    handle = property(lambda self: self.obj)


@public
class JavaException(Exception):

    """Can be a real java exception, or just an exception from the wrapper."""

    classname    = None  # The classname of the exception
    innermessage = None  # The message of the inner exception
    stacktrace   = None  # The stack trace of the inner exception

    def __init__(self, message, classname=None, innermessage=None, stacktrace=None):

        super(JavaException, self).__init__(message)
        self.classname    = classname
        self.innermessage = innermessage
        self.stacktrace   = stacktrace

    @classmethod
    def __exception__(cls, jexc):

        # jexc: jt.jvm.JException

        classname  = jexc.getClass().getName()
        message    = jexc.getMessage()
        stacktrace = cls._exception_trace_messages(jexc)

        return cls("JVM exception occurred: {}".format(
                   message if message is not None else classname),
                   classname, message, stacktrace)

    @classmethod
    def _exception_trace_messages(cls, jexc, stacktrace=None):

        if stacktrace is None: stacktrace = []

        # Get the array of StackTraceElements.
        frames = jexc.getStackTrace()
        if not frames:
            return stacktrace

        # Add Throwable.toString() before descending stack trace messages.
        describe = jexc.toString()
        if len(stacktrace) > 0:
            # If this is not the top-of-the-trace then this is a cause.
            stacktrace.append("Caused by:")
        stacktrace.append(describe)

        # Append stack trace messages
        for item in frames:
            # Get the string returned from the 'toString()' method of the next frame
            # and append it to the error message.
            stacktrace.append(item.toString())

        # If 'jexc' has a cause then append the stack trace messages from the cause.
        cause = jexc.getCause()
        if cause:
            cls._exception_trace_messages(cause, stacktrace)

        return stacktrace
