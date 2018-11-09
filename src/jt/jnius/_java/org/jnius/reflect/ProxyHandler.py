# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import unicode_literals
from __future__ import absolute_import

import traceback

from ......           import jni
from ......jvm.jframe import JFrame
from ......jvm.jhost  import JHost
from ......jvm.java   import throwJavaException

from ....._jvm        import JVM
from ....._conversion import convert_jobject_to_python


# Class: com.jt.reflect.ProxyHandler

# Method: native Object invoke(long target, Object proxy, java.lang.reflect.Method method, Object[] args);

@jni.method("(JLjava/lang/Object;Ljava/lang/reflect/Method;[Ljava/lang/Object;)Ljava/lang/Object;")
def invoke(env, this,
           target, jproxy, jmethod, jargs):

    global __convert_signature

    proxy = jni.from_oid(target)

    jt_jvm = JVM.jvm
    jenv = env[0]
    try:
        method, args = None, []
        try:
            method = jt_jvm.JMethod(None, jmethod, borrowed=True)

            param_signatures = tuple(x.getSignature() for x in method.getParameterTypes())

            with JFrame(jenv, len(param_signatures)):
                for idx, par_signature in enumerate(param_signatures):
                    jarg = jenv.GetObjectArrayElement(jargs, idx)
                    jarg = jt_jvm.JObject(None, jarg, borrowed=True) if jarg else None
                    par_signature = __convert_signature.get(par_signature, par_signature)
                    parg = convert_jobject_to_python(par_signature, jarg)
                    args.append(parg)

                result = proxy(method, *args)

                if result is None:
                    return None
                else:
                    # if not isinstance(result, JB_Object):
                    #     raise TypeError("Must be JB_Object")
                    if not hasattr(result, "handle") or not result.handle.value:
                        print("@@@@@@*******************@@@@@@@@@")
                    return jenv.NewGlobalRef(result.handle)

        finally:
            del method, args
    except Exception as exc:
        traceback.print_exc()

    return None

# convert java argument to python object
# native java type are given with java.lang.*,
# even if the signature say it's a native type.
__convert_signature = {
    "Z": "Ljava/lang/Boolean;",
    "C": "Ljava/lang/Character;",
    "B": "Ljava/lang/Byte;",
    "S": "Ljava/lang/Short;",
    "I": "Ljava/lang/Integer;",
    "J": "Ljava/lang/Long;",
    "F": "Ljava/lang/Float;",
    "D": "Ljava/lang/Double;",
}

# Method: native void initialize(long target);

@jni.method("(J)V")
def initialize(env, this,
               target):
    pass

# Method: native void release(long target);

@jni.method("(J)V")
def release(env, this,
            target):
    pass


__jnimethods__ = (
    invoke,
    initialize,
    release,
)
