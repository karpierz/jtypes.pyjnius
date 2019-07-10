# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

"""
signatures.py
=============

A handy API for writing JNI signatures easily

Author: chrisjrn

This module aims to provide a more human-friendly API for
wiring up Java proxy methods in PyJnius.

You can use the signature function to produce JNI method
signautures for methods; passing PyJnius JavaClass classes
as return or argument types; provided here are annotations
representing Java's primitive and array times.

Methods can return just a standard primitive type:

>>> signature(jint, ())
'()I'

>>> s.signature(jvoid, [jint])
'(I)V'

Or you can use autoclass proxies to specify Java classes
for return types.

>>> from jt.jnius import autoclass
>>> String = autoclass("java.lang.String")
>>> signature(String, ())
'()Ljava/lang/String;'

"""

from __future__ import absolute_import

import abc

from ..jvm.lib.compat import *
from ..jvm.lib import metaclass
from ..jvm.lib import annotate
from ..jvm.lib import public

from ._main import JavaClass, java_method


@metaclass(abc.ABCMeta)
class _JavaSignaturePrimitive(object):
    """ Type specifiers for primitives """


def _MakeSignaturePrimitive(name, spec):

    class __Primitive(_JavaSignaturePrimitive):
        """ PyJnius signature for Java %s type """ % name
        _name = name
        _spec = spec
    __Primitive.__name__ = "j" + name

    return __Primitive


public(jboolean = _MakeSignaturePrimitive("boolean", "Z"))
public(jchar    = _MakeSignaturePrimitive("char",    "C"))
public(jbyte    = _MakeSignaturePrimitive("byte",    "B"))
public(jshort   = _MakeSignaturePrimitive("short",   "S"))
public(jint     = _MakeSignaturePrimitive("int",     "I"))
public(jlong    = _MakeSignaturePrimitive("long",    "J"))
public(jfloat   = _MakeSignaturePrimitive("float",   "F"))
public(jdouble  = _MakeSignaturePrimitive("double",  "D"))
public(jvoid    = _MakeSignaturePrimitive("void",    "V"))
public(JArray   = lambda of_type: _MakeSignaturePrimitive("array", "[" + _jni_type_spec(of_type)))


@public
def with_signature(returns, takes):

    """Alternative version of @java_method that takes JavaClass
    objects to produce the method signature."""

    return java_method(signature(returns, takes))


@public
def signature(returns, takes):

    """Produces a JNI method signature, taking the provided arguments
    and returning the given return type."""

    return "(" + "".join(_jni_type_spec(arg) for arg in takes) + ")" + _jni_type_spec(returns)


def _jni_type_spec(jclass):

    """Produces a JNI type specification string for the given argument.
    If the argument is a jnius.JavaClass, it produces the JNI type spec
    for the class. Signature primitives return their stored type spec."""

    if issubclass(jclass, JavaClass):
        return "L" + jclass.__javaclass__ + ";"
    elif issubclass(jclass, _JavaSignaturePrimitive):
        return jclass._spec
    else:
        return None
