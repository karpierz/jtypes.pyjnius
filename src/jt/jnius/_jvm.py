# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import absolute_import

import os

from ..jvm.lib.compat import *
from ..jvm.lib import annotate, Optional
from ..jvm.lib import public
from ..jvm     import jni

from ..jvm import JVM as _JVM


@annotate(Optional[_JVM])
def get_jvm():

    # first call, init.
    if not JVM.jenv:
        from . import _platform
        JVM.jvm = JVM()
        _platform.start_jvm(JVM.jvm)
        _, JVM.jenv = JVM.jvm
        if not JVM.jenv:
            return None

    return JVM.jvm


@annotate(Optional[jni.JNIEnv])
def get_jenv():

    jvm = get_jvm()
    if jvm is not None:
        _, jenv = jvm
        return jenv
    else:
        return None


@public
def detach():

    JVM.jvm.detachThread()


# from https://gist.github.com/tito/09c42fb4767721dc323d
if "ANDROID_ARGUMENT" in os.environ:
    # on android, catch all exception to ensure about a jnius.detach
    import threading
    orig_thread_run = threading.Thread.run

    def jnius_thread_hook(*args, **kwargs):
        try:
            return orig_thread_run(*args, **kwargs)
        finally:
            detach()

    threading.Thread.run = jnius_thread_hook


class JVM(_JVM):

    """Represents the Java virtual machine"""

    jvm  = None  # Optional[jt.jvm.JVM]
    jenv = None  # Optional[jni.JNIEnv]

    def __init__(self, dll_path=None):

        from ._typehandler import TypeHandler

        self._dll_path = None
        self.load(dll_path)
        self.type_handler = TypeHandler()

    def load(self, dll_path=None):

        from ..jvm.platform import JVMFinder
        from ..jvm          import EStatusCode
        from ._jclass       import JavaException

        if dll_path is not None:
            self._dll_path = dll_path

        if self._dll_path is None:
            finder = JVMFinder()
            self._dll_path = finder.get_jvm_path()

        super(JVM, self).__init__(self._dll_path)
        self.JavaException = JavaException
        self.ExceptionsMap = {
            EStatusCode.ERR:       JavaException,
            EStatusCode.EDETACHED: JavaException,
            EStatusCode.EVERSION:  JavaException,
            EStatusCode.ENOMEM:    JavaException,
            EStatusCode.EEXIST:    JavaException,
            EStatusCode.EINVAL:    JavaException,
        }

    def start(self, *jvmoptions, **jvmargs):

        result = super(JVM, self).start(*jvmoptions, **jvmargs)

        from ._java import jnijnius

        ProxyHandler = jnijnius.jnius_reflect_ProxyHandler()

        with self as (jvm, jenv):
            ProxyHandler.initialize(jenv)
        self.type_handler.start()

        return result

    def shutdown(self):

        self.type_handler.stop()
        super(JVM, self).shutdown()


# eof
