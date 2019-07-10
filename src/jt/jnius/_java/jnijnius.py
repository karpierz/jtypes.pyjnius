# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ...jvm.lib.compat import *
from ...jvm.lib import annotate
from ...        import jni

from ...jvm.java.jnij import jnij
from ...jvm.java      import registerNatives
from ...jvm.java      import unregisterNatives


class jnius_reflect_ProxyHandler(jnij):

    @annotate(jenv=jni.JNIEnv)
    def initialize(self, jenv):

        from .org.jnius.reflect import ProxyHandler
        unregisterNatives(jenv, "com.jt.reflect.ProxyHandler")
        registerNatives(jenv,   "com.jt.reflect.ProxyHandler", ProxyHandler)
