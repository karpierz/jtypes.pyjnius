# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import absolute_import

from functools import partial
import traceback

from ..jvm.lib.compat import *
from ..jvm.lib.compat import PY2
from ..jvm.lib import annotate
from ..jvm.lib import public
from ..        import jni


@public
class java_implementer(object):

    def __new__(cls, *interfaces):

        self = super(java_implementer, cls).__new__(cls)
        self.interfaces = interfaces
        return self

    def __call__(self, klass):

        if self.interfaces:
            klass.__javainterfaces__ = self.interfaces
        return klass
       #return metaclass(MetaJavaBase)(klass)


@public
class java_method(object):

    def __new__(cls, signature, name=None):

        self = super(java_method, cls).__new__(cls)
        self.signature = signature
        self.name      = name
        return self

    def __get__(self, this, cls):

        return partial(self.__call__, this)

    def __call__(self, method):

        method.__javasignature__ = self.signature
        method.__javaname__      = self.name
        return method


@public
class PythonJavaClass(object):

    """Base class to create a java class from python"""

    def __new__(cls, *args, **kwargs):

        self = super(PythonJavaClass, cls).__new__(cls)
        self.j_self = None
        return self

    jcls = property(lambda self: jni.obj(jni.jclass))

    def __init__(self, *args, **kwargs):

        self._init_j_self_ptr()

    def _init_j_self_ptr(self):

        from ._func import find_javaclass
        from ._util import parse_definition

        jinterfaces = [find_javaclass(iname.replace("/", "."))
                       for iname in self.__javainterfaces__]
        javacontext = getattr(self, "__javacontext__", "system")
        self.j_self = _create_proxy_instance(self, jinterfaces, javacontext)
        # discover all the java method implemented
        self.__javamethods__ = {}
        for aname in dir(self):
            attr = getattr(self, aname)
            if callable(attr) and hasattr(attr, "__javasignature__"):
                signature = parse_definition(attr.__javasignature__)
                self.__javamethods__[(attr.__javaname__ or aname, signature)] = attr

    def __call__(self, method, *args):

        try:
            # search the java method

            method_name      = method.getName()
            return_signature = method.getReturnType().getSignature()
            param_signatures = tuple(x.getSignature() for x in method.getParameterTypes())

            key = (method_name, (return_signature, param_signatures))
            try:
                py_method = self.__javamethods__[key]
            except KeyError:
                print("\n===== Python/java method missing ======"
                      "\nPython class: {!r}"
                      "\nJava method name: {}"
                      "\nSignature: ({}){}"
                      "\n======================================="
                      "\n".format(self, method_name,
                                  "".join(param_signatures), return_signature))
                raise NotImplementedError("The method {} is not implemented".format(key))

            result = py_method(*args)

        except Exception:
            traceback.print_exc()
            return None

        # convert back to the return type

        # did python returned a "native" type ?
        if return_signature == "Ljava/lang/Object;":
            # generic object, try to manually convert it
            return_signature = self.__convert_signature.get(type(result), return_signature)

        thandler = method.jvm.type_manager.get_handler(return_signature)
        return thandler.toJava(result)

    __convert_signature = {
        bool:  "Z",
        int:   "I" if PY2 else "J",
        long:  "J",
        float: "D",
    }


def _create_proxy_instance(pjobj, jinterfaces, javacontext):

    # now we need to create a proxy and pass it an invocation handler

    from .reflect import autoclass

    # create the proxy and pass it the invocation handler
    if javacontext == "app":
        Thread       = autoclass("java.lang.Thread")
        class_loader = Thread.currentThread().getContextClassLoader()
    elif javacontext == "system":
        ClassLoader  = autoclass("java.lang.ClassLoader")
        class_loader = ClassLoader.getSystemClassLoader()
    else:
        raise Exception("Invalid __javacontext__ {}, "
                        "must be app or system.".format(javacontext))

    Proxy        = autoclass("java.lang.reflect.Proxy")
    ProxyHandler = autoclass("com.jt.reflect.ProxyHandler")
    return Proxy.newProxyInstance(class_loader, jinterfaces, ProxyHandler(id(pjobj)))
