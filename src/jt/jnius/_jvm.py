# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import absolute_import

import os
import atexit

from ..jvm.lib.compat import *
from ..jvm.lib import annotate, Optional
from ..jvm.lib import public
from ..jvm.lib import classproperty
from ..jvm.lib import platform
from ..        import jni

from ..jvm import JVM as _JVM


@public
def detach():

    JVM._jvm.detachThread()


# from https://gist.github.com/tito/09c42fb4767721dc323d
if platform.is_android:
    # on android, catch all exception to ensure about a jnius.detach
    import threading
    orig_thread_run = threading.Thread.run

    def jnius_thread_hook(*args, **kwargs):
        try:
            return orig_thread_run(*args, **kwargs)
        finally:
            detach()

    threading.Thread.run = jnius_thread_hook
del platform


@public
class JVM(_JVM):

    """Represents the Java virtual machine"""

    @classproperty
    @annotate(Optional['JVM'])
    def jvm(cls):

        # first call, init.
        if not JVM._jenv:
            from . import _platform
            jvm = JVM()
            _platform.start_jvm(jvm)
            atexit.register(_platform.stop_jvm, jvm)

        return JVM._jvm if JVM._jenv else None

    @classproperty
    @annotate(Optional[jni.JNIEnv])
    def jenv(cls):

        jvm = JVM.jvm
        if jvm is not None:
            _, jenv = jvm
            return jenv
        else:
            return None

    _jvm  = None  # Optional[jt.jvm.JVM]
    _jenv = None  # Optional[jni.JNIEnv]

    def __init__(self, dll_path=None):

        from ._typemanager import TypeManager

        self._dll_path = None
        self._load(dll_path)
        self._create()
        self.type_manager = TypeManager()

    def start(self, *jvmoptions, **jvmargs):

        _, jenv = result = super(JVM, self).start(*jvmoptions, **jvmargs)
        JVM._jvm, JVM._jenv = self, jenv
        self._initialize(jenv)
        self.type_manager.start()
        return result

    def shutdown(self):

        self.type_manager.stop()
        _, jenv = self
        self._dispose(jenv)
        super(JVM, self).shutdown()
        JVM._jvm = JVM._jenv = None

    def _load(self, dll_path=None):

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

    def _create(self):

        from ._java import jnijnius
        self.ProxyHandler = jnijnius.jnius_reflect_ProxyHandler()

    @annotate(jenv=jni.JNIEnv)
    def _initialize(self, jenv):

        self.ProxyHandler.initialize(jenv)

    @annotate(jenv=jni.JNIEnv)
    def _dispose(self, jenv):

        self.ProxyHandler.dispose(jenv)
