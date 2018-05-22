# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import unicode_literals
from __future__ import absolute_import

from ......jvm        import jni
from ......jvm.jframe import JFrame
from ......jvm.jhost  import JHost
from ......jvm.java   import throwJavaException

from ....._jvm import get_jvm


# Class: com.jt.reflect.ProxyHandler

# Method: native Object invoke(long target, Object proxy,
#                              java.lang.reflect.Method method, Object[] args);

@jni.method("(JLjava/lang/Object;Ljava/lang/reflect/Method;[Ljava/lang/Object;)Ljava/lang/Object;")
def invoke(env, this,
           target, jproxy, jmethod, jargs):

    from ....._conversion import convert_jobject_to_python

    proxy = jni.from_oid(target)

    jt_jvm = get_jvm()
    jenv = env[0]
    try:
        method, args = None, []
        try:
            method = jt_jvm.JMethod(None, jmethod, borrowed=True)

            arg_signatures = tuple(x.getSignature() for x in method.getParameterTypes())
            argcnt = len(arg_signatures)

            # convert java argument to python object
            # native java type are given with java.lang.*,
            # even if the signature say it's a native type.
            convert_signature = {
                "Z": "Ljava/lang/Boolean;",
                "B": "Ljava/lang/Byte;",
                "C": "Ljava/lang/Character;",
                "S": "Ljava/lang/Short;",
                "I": "Ljava/lang/Integer;",
                "J": "Ljava/lang/Long;",
                "F": "Ljava/lang/Float;",
                "D": "Ljava/lang/Double;",
            }

            with JFrame(jenv, argcnt):
                for idx in range(argcnt):
                    jarg = jenv.GetObjectArrayElement(jargs, idx)
                    jarg = jt_jvm.JObject(None, jarg, borrowed=True) if jarg else None
                    arg_signature = arg_signatures[idx]
                    arg_signature = convert_signature.get(arg_signature, arg_signature)
                    parg = convert_jobject_to_python(arg_signature, jarg)
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
    except Exception:
        import traceback
        traceback.print_exc()

    return None

# Method: native void finalize(long target);

@jni.method("(J)V")
def finalize(env, this,
             target):

    proxy = jni.from_oid(target)

    with JHost.CallbackState():
        pass
