# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import absolute_import

import ctypes as ct

from ..jvm.lib.compat import *
from ..jvm.lib.compat import PY2
from ..jvm.lib import annotate, Optional, Union, Tuple
from ..        import jni

from ..jvm.jframe  import JFrame
from ..jvm.jstring import JString

from ._jclass      import MetaJavaClass, JavaClass, JavaObject, JavaException
from ._nativetypes import ByteArray
from ._jvm         import JVM

str_types = (builtins.str, str)


@annotate(definition=str, jobj=Optional['jt.jvm.JObject'])
def convert_jobject_to_python(definition, jobj):

    # Convert a Java Object to a Python object, according to the definition.
    # If the definition class is a java.lang.Object, then try to determine
    # what is it exactly.

    if jobj is None:
        return None

    obj_typename  = definition[1:-1]
    obj_classname = obj_typename.replace("/", ".")

    if obj_classname == "java.lang.Object":
        # we got a generic object, lookup for the real name instead.
        obj_classname = jobj.getClass().getName()
        obj_typename  = obj_classname.replace(".", "/")
        definition    = obj_typename

    if definition[0] == "[":
        jarr = jobj.asArray(own=False)
        return convert_jarray_to_python(definition, jarr)

    # definition[0] != "[":

    # XXX what about others native type?
    # It seem, in case of the proxy, that they are never passed directly,
    # and always passed as "class" type instead.
    # Ie, B would be passed as Ljava/lang/Character;

    # XXX should be deactivable from configuration
    # ie, user might not want autoconvertion of lang classes.

    if obj_classname == "java.lang.Boolean":
        return jobj.booleanValue()
    elif obj_classname == "java.lang.Character":
        return ord(jobj.charValue())
    elif obj_classname == "java.lang.Byte":
        return jobj.byteValue()
    elif obj_classname == "java.lang.Short":
        return jobj.shortValue()
    elif obj_classname == "java.lang.Integer":
        return jobj.intValue()
    elif obj_classname == "java.lang.Long":
        return jobj.longValue()
    elif obj_classname == "java.lang.Float":
        return jobj.floatValue()
    elif obj_classname == "java.lang.Double":
        return jobj.doubleValue()
    elif obj_classname == "java.lang.String":
        with jobj.jvm as (_, jenv):
            py_uni = JString(jenv, jobj.handle, own=False).str
        #!!! a moze builtins.str(py_uni) ??? !!!
        return py_uni.encode("utf-8") if PY2 else py_uni
    elif obj_classname == "java.lang.CharSequence":
        py_uni = jobj.toString()
        #!!! a moze builtins.str(py_uni) ??? !!!
        return py_uni.encode("utf-8") if PY2 and py_uni is not None else py_uni
    else:
        cls = MetaJavaClass.get_javaclass(obj_typename)
        if not cls:
            if obj_classname.startswith("$Proxy"):
                # Only for $Proxy on Android, don't use autoclass. The dalvik vm is
                # not able to give us introspection on that one (FindClass return None).
                from .reflect import Object
                cls = Object
            else:
                from .reflect import autoclass
                cls = autoclass(obj_classname)
        obj = cls(noinstance=True)
        obj._instantiate_from(jobj)
        return obj


@annotate(definition=str, jarr=Optional['jt.jvm.JArray'])
def convert_jarray_to_python(definition, jarr):

    jvm = JVM.jvm

    if jarr is None:
        return None

    elem_definition = definition[1:]
    r = elem_definition[0]

    thandler = jvm.type_manager.get_handler(r)

    if r == "Z":

        buf = thandler.getArrayBuffer(jarr).buf
        try:
            return [bool(buf[i]) for i in range(len(jarr))]
        finally:
            thandler.releaseArrayBuffer(jarr, buf)

    elif r == "C":

        buf = thandler.getArrayBuffer(jarr).buf
        try:
            #!!! tu sprawdzic ta konwersje !!!
            return [builtins.str(buf[i]) for i in range(len(jarr))]
        finally:
            thandler.releaseArrayBuffer(jarr, buf)

    elif r == "B":

        ret = ByteArray()
        ret._set_buffer(jarr)
        return ret

    elif r in ("S", "I", "J", "F", "D"):

        buf = thandler.getArrayBuffer(jarr).buf
        try:
            return buf[0:len(jarr)]
        finally:
            thandler.releaseArrayBuffer(jarr, buf)

    elif r == "L":

        ret  = []
        size = len(jarr)
        with jarr.jvm as (jvm, jenv), JFrame(jenv) as jfrm:
            for idx in range(size):
                if not (idx % 256): jfrm.reset(256)
                jobj = jenv.GetObjectArrayElement(jarr.handle, idx)
                jobj = jarr.jvm.JObject(None, jobj, own=False) if jobj else None
                ret.append(convert_jobject_to_python(elem_definition, jobj))
        return ret

    elif r == "[":

        ret  = []
        size = len(jarr)
        with jarr.jvm as (jvm, jenv), JFrame(jenv) as jfrm:
            for idx in range(size):
                if not (idx % 256): jfrm.reset(256)
                jobj = jenv.GetObjectArrayElement(jarr.handle, idx)
                jobj = jarr.jvm.JArray(None, jobj, own=False) if jobj else None
                ret.append(convert_jarray_to_python(elem_definition, jobj))
        return ret

    else:
        raise JavaException("Invalid return definition for array")


@annotate('jt.jvm.JArray', definition=bytes)#, jenv=Optional[jni.JNIEnv])
def convert_python_to_jarray(definition, pyarr, jenv=None):

    global __to_jarray_conversions

    jvm = JVM.jvm
    if jenv is None: jenv = JVM.jenv

    elem_definition = definition[1:]

    if elem_definition == "Ljava/lang/Object;" and len(pyarr) > 0:
        # then the method will accept any array type as param
        # let's be as precise as we can
        elem_definition = next((override
                                for ttype, override in __to_jarray_conversions.items()
                                if isinstance(pyarr[0], ttype)), elem_definition)

    thandler = jvm.type_manager.get_handler(elem_definition)

    if elem_definition in ("Z", "C", "S", "I", "J", "F", "D"):

        size = len(pyarr)
        jarr = thandler.newArray(size)
        for idx, elem in enumerate(pyarr):
            thandler.setElement(jarr, idx, elem)
        return jarr

    elif elem_definition == "B":

        size = len(pyarr)
        jarr = thandler.newArray(size)
        if isinstance(pyarr, ByteArray):
            jenv.SetByteArrayRegion(jarr.handle, 0, size,
                                    jni.cast(pyarr._buf, jni.POINTER(jni.jbyte)))
        else:
            for idx, elem in enumerate(pyarr):
                thandler.setElement(jarr, idx, elem)
        return jarr

    elif elem_definition[0] == "L":

        obj_classname = elem_definition[1:-1].replace("/", ".")

        try:
            jclass = jvm.JClass.forName(obj_classname)
        except:
            raise JavaException("Cannot create array with a class not found {!r}".format(
                                obj_classname))

        size = len(pyarr)
        jarr = jvm.JArray.newObjectArray(size, jclass)
        # iterate over each Python array element and add it to Object[].
        for idx, elem in enumerate(pyarr):
            if elem is None:
                jenv.SetObjectArrayElement(jarr.handle, idx, None)
            elif isinstance(elem, str_types) and obj_classname in ("java.lang.String",
                                                                   "java.lang.CharSequence",
                                                                   "java.lang.Object"):
                py_uni = elem.decode("utf-8") if isinstance(elem, bytes) else elem
                jstr = jvm.JObject.newString(py_uni)
                #if jstr == NULL:
                #    check_exception(j_env) # raise error as JavaException
                jenv.SetObjectArrayElement(jarr.handle, idx, jstr.handle)
            # isinstance(elem, type) will return False ...and it's really weird
            elif isinstance(elem, (tuple, list)):
                jarr_nested = convert_python_to_jarray("["+elem_definition, elem, jenv=jenv)
                jenv.SetObjectArrayElement(jarr.handle, idx, jarr_nested.handle)
            # no local refs to delete for class, type and object
            elif isinstance(elem, JavaClass):
                _check_assignable_from(obj_classname, elem)
                jclass = elem.j_self
                jenv.SetObjectArrayElement(jarr.handle, idx, jclass.handle)
            elif isinstance(elem, JavaObject):
                jenv.SetObjectArrayElement(jarr.handle, idx, elem.handle)
            elif isinstance(elem, type):
                jenv.SetObjectArrayElement(jarr.handle, idx, elem.jcls if elem.jcls else None)
            else:
                raise JavaException("Invalid variable {!r} used for L array {!r}".format(
                                    pyarr, elem_definition))
        return jarr

    elif elem_definition[0] == "[":

        size   = len(pyarr)
        jclass = convert_python_to_jarray(elem_definition, pyarr[0], jenv=jenv).getClass()
        jarr = jvm.JArray.newObjectArray(size, jclass)
        for idx, elem in enumerate(pyarr):
            jarr_nested = convert_python_to_jarray(elem_definition, elem, jenv=jenv)
            jenv.SetObjectArrayElement(jarr.handle, idx, jarr_nested.handle)
        return jarr

    else:
        raise JavaException("Invalid array definition {!r} for variable {!r}".format(
                            elem_definition, pyarr))

__to_jarray_conversions = {
    bool:  "Z",
    int:   "I",
    long:  "J",
    float: "F",
    str:   "Ljava/lang/String;",
    bytes: "Ljava/lang/String;" if PY2 else "B",
}


__assignable_from_cache = {}
__assignable_from_order = 0

@annotate(classname=bytes, jc=JavaClass)
def _check_assignable_from(classname, jc):

    global __assignable_from_cache
    global __assignable_from_order

    jvm  = JVM.jvm
    jenv = JVM.jenv

    # first call, we need to get over the libart issue, which implemented
    # IsAssignableFrom the wrong way.
    # Ref: https://github.com/kivy/pyjnius/issues/92
    # Google Bug: https://android.googlesource.com/platform/art/+/1268b74%5E!/
    if __assignable_from_order == 0:

        String = jvm.JClass.forName("java.lang.String")
        Object = jvm.JClass.forName("java.lang.Object")
        # -1 means that bug triggered. IsAssignableFrom said we can do
        # things like: String a = Object()
        __assignable_from_order = -1 if String.isAssignableFrom(Object) else 1
        del String
        del Object

    if classname == "java.lang.Object":
        # if we have a JavaObject, it's always ok.
        return

    jc_classname = jc.__javaclass__.replace("/", ".")

    # FIXME Android/libART specific check
    # check_jni.cc crash when calling the IsAssignableFrom with
    # com/jt/reflect/ProxyHandler java/lang/reflect/InvocationHandler
    # Because we know it's ok, just return here.
    if (classname == "java.lang.reflect.InvocationHandler" and
        jc_classname == "com.jt.reflect.ProxyHandler"):
        return

    if jc_classname == classname:
        # if the signature is a direct match, it's ok too :)
        return

    # if we already did the test before, use the cache result!
    result = __assignable_from_cache.get((jc_classname, classname))
    if result is None:

        # we got an object that doesn't match with the classname
        # check if we can use it.

        try:
            jclass = jvm.JClass.forName(classname)
        except:
            raise JavaException("Unable to found the class for {!r}".format(
                                classname))
        try:
            result = (jclass.isAssignableFrom(jc._jclass)
                      if __assignable_from_order == 1 else
                      jc._jclass.isAssignableFrom(jclass))
        except JavaException:
            result = False
            jenv.ExceptionDescribe()

        __assignable_from_cache[(jc_classname, classname)] = result

    if not result:
        raise JavaException("Invalid instance of {!r} passed for a {!r}".format(
                            jc_classname, classname))
