# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ..jvm.lib.compat import *
from ..jvm.lib import annotate
from ..jvm.lib import public

from ._constants import EJavaModifiers
from ._main import (java_class, MetaJavaClass, JavaClass, JavaField, JavaStaticField,
                    JavaMethod, JavaStaticMethod, JavaMultipleMethod, JavaException,
                    find_javaclass)


@java_class("java/lang/Class")
class Class(object):

    desiredAssertionStatus  = JavaMethod("()Z")
    forName = JavaMultipleMethod([("(Ljava/lang/String,Z,Ljava/lang/ClassLoader;)Ljava/langClass;", True, False),
                                  ("(Ljava/lang/String;)Ljava/lang/Class;",                         True, False)])
    getClassLoader          = JavaMethod("()Ljava/lang/ClassLoader;")
    getClasses              = JavaMethod("()[Ljava/lang/Class;")
    getComponentType        = JavaMethod("()Ljava/lang/Class;")
    getConstructor          = JavaMethod("([Ljava/lang/Class;)Ljava/lang/reflect/Constructor;")
    getConstructors         = JavaMethod("()[Ljava/lang/reflect/Constructor;")
    getDeclaredClasses      = JavaMethod("()[Ljava/lang/Class;")
    getDeclaredConstructor  = JavaMethod("([Ljava/lang/Class;)Ljava/lang/reflect/Constructor;")
    getDeclaredConstructors = JavaMethod("()[Ljava/lang/reflect/Constructor;")
    getDeclaredField        = JavaMethod("(Ljava/lang/String;)Ljava/lang/reflect/Field;")
    getDeclaredFields       = JavaMethod("()[Ljava/lang/reflect/Field;")
    getDeclaredMethod       = JavaMethod("(Ljava/lang/String,[Ljava/lang/Class;)Ljava/lang/reflect/Method;")
    getDeclaredMethods      = JavaMethod("()[Ljava/lang/reflect/Method;")
    getDeclaringClass       = JavaMethod("()Ljava/lang/Class;")
    getField                = JavaMethod("(Ljava/lang/String;)Ljava/lang/reflect/Field;")
    getFields               = JavaMethod("()[Ljava/lang/reflect/Field;")
    getInterfaces           = JavaMethod("()[Ljava/lang/Class;")
    getMethod               = JavaMethod("(Ljava/lang/String,[Ljava/lang/Class;)Ljava/lang/reflect/Method;")
    getMethods              = JavaMethod("()[Ljava/lang/reflect/Method;")
    getModifiers            = JavaMethod("()[I")
    getName                 = JavaMethod("()Ljava/lang/String;")
    getPackage              = JavaMethod("()Ljava/lang/Package;")
    getProtectionDomain     = JavaMethod("()Ljava/security/ProtectionDomain;")
    getResource             = JavaMethod("(Ljava/lang/String;)Ljava/net/URL;")
    getResourceAsStream     = JavaMethod("(Ljava/lang/String;)Ljava/io/InputStream;")
    getSigners              = JavaMethod("()[Ljava/lang/Object;")
    getSuperclass           = JavaMethod("()Ljava/lang/reflect/Class;")
    isArray                 = JavaMethod("()Z")
    isAssignableFrom        = JavaMethod("(Ljava/lang/reflect/Class;)Z")
    isInstance              = JavaMethod("(Ljava/lang/Object;)Z")
    isInterface             = JavaMethod("()Z")
    isPrimitive             = JavaMethod("()Z")
    newInstance             = JavaMethod("()Ljava/lang/Object;")
    toString                = JavaMethod("()Ljava/lang/String;")


@java_class("java/lang/Object")
class Object(object):

    getClass = JavaMethod("()Ljava/lang/Class;")
    hashCode = JavaMethod("()I")


@java_class("java/lang/reflect/Modifier")
class Modifier(object):

    isAbstract     = JavaStaticMethod("(I)Z")
    isFinal        = JavaStaticMethod("(I)Z")
    isInterface    = JavaStaticMethod("(I)Z")
    isNative       = JavaStaticMethod("(I)Z")
    isPrivate      = JavaStaticMethod("(I)Z")
    isProtected    = JavaStaticMethod("(I)Z")
    isPublic       = JavaStaticMethod("(I)Z")
    isStatic       = JavaStaticMethod("(I)Z")
    isStrict       = JavaStaticMethod("(I)Z")
    isSynchronized = JavaStaticMethod("(I)Z")
    isTransient    = JavaStaticMethod("(I)Z")
    isVolatile     = JavaStaticMethod("(I)Z")


@java_class("java/lang/reflect/Field")
class Field(object):

    getName      = JavaMethod("()Ljava/lang/String;")
    toString     = JavaMethod("()Ljava/lang/String;")
    getType      = JavaMethod("()Ljava/lang/Class;")
    getModifiers = JavaMethod("()I")


@java_class("java/lang/reflect/Constructor")
class Constructor(object):

    toString          = JavaMethod("()Ljava/lang/String;")
    getParameterTypes = JavaMethod("()[Ljava/lang/Class;")
    getModifiers      = JavaMethod("()I")
    isVarArgs         = JavaMethod("()Z")


@java_class("java/lang/reflect/Method")
class Method(object):

    getName           = JavaMethod("()Ljava/lang/String;")
    toString          = JavaMethod("()Ljava/lang/String;")
    getParameterTypes = JavaMethod("()[Ljava/lang/Class;")
    getReturnType     = JavaMethod("()Ljava/lang/Class;")
    getModifiers      = JavaMethod("()I")
    isVarArgs         = JavaMethod("()Z")


@public
def autoclass(clsname):

    from ._jvm import JVM

    jvm = JVM.jvm

    cls = MetaJavaClass.get_javaclass(clsname.replace(".", "/"))
    if cls:
        return cls

    try:
        # name = clsname.encode("utf-8").translate(jvm.JClass.name_utrans).decode("utf-8")
        jclass = jvm.JClass.forName(clsname.replace("/", "."))
    except:
        raise JavaException("Class not found {!r}".format(clsname))

    clsdict = {}

    definitions = []
    for constructor in jclass.getConstructors():
        signature  = constructor.getSignature()
        is_varargs = constructor.isVarArgs()
        definitions.append((signature, is_varargs))
    clsdict["__javaconstructor__"] = definitions

    methods       = jclass.getMethods()
    methods_names = [method.getName() for method in methods]
    for method, method_name in zip(methods, methods_names):
        if method_name in clsdict:
            continue
        if methods_names.count(method_name) == 1:
            # only one method available
            mods = method.getModifiers()
            is_static  = EJavaModifiers.STATIC in mods
            signature  = method.getSignature()
            is_varargs = method.isVarArgs()
            clsdict[method_name] = (JavaStaticMethod(signature, varargs=is_varargs)
                                    if is_static else
                                    JavaMethod(signature, varargs=is_varargs))
            if method_name != "getClass" and bean_getter(method_name) and len(method.getParameterTypes()) == 0:
                clsdict[lower_name(method_name[2 if method_name.startswith("is") else 3:])] = \
                        (lambda n: property(lambda self: getattr(self, n)()))(method_name)
        else:
            # multiple signatures
            definitions = []
            for method, subname in zip(methods, methods_names):
                if subname != method_name:
                    continue
                mods = method.getModifiers()
                is_static  = EJavaModifiers.STATIC in mods
                signature  = method.getSignature()
                is_varargs = method.isVarArgs()
                definitions.append((signature, is_static, is_varargs))
            clsdict[method_name] = JavaMultipleMethod(definitions)

    def _getitem(self, idx):
        try:
            return self.get(idx)
        except JavaException as exc:
            # initialize the subclass before getting the Class.forName
            # otherwise isInstance does not know of the subclass
            mock_exception_object = autoclass(exc.classname)()
            # python for...in iteration checks for end of list by waiting for IndexError
            raise IndexError() if find_javaclass("java.lang.IndexOutOfBoundsException"
                                                ).isInstance(mock_exception_object) else exc

    for iclass in jclass.getInterfaces():
        if iclass.getName() == "java.util.List":
            clsdict["__getitem__"] = _getitem
            clsdict["__len__"]     = lambda self: self.size()
            break

    for field in jclass.getFields():
        field_name = field.getName()
        mods = field.getModifiers()
        is_static = EJavaModifiers.STATIC in mods
        signature = field.getSignature()
        clsdict[field_name] = (JavaStaticField(signature)
                               if is_static else
                               JavaField(signature))

    clsdict["__javaclass__"] = clsname.replace(".", "/")

    return MetaJavaClass(clsname, (), clsdict)


def get_signature(cls):

    return cls.j_self.getSignature()


def bean_getter(s):

    return ((s.startswith("get") and len(s) > 3 and s[3].isupper()) or
            (s.startswith("is")  and len(s) > 2 and s[2].isupper()))

def lower_name(s):

    return s[:1].lower() + s[1:] if s else ""


registers = []

@public
def ensureclass(clsname):

    global registers
    if clsname in registers:
        return
    if MetaJavaClass.get_javaclass(clsname.replace(".", "/")):
        return
    registers.append(clsname)
    autoclass(clsname)
