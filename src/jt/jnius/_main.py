# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

"""
Java wrapper
============

With this module, you can create Python class that reflects a Java class, and use
it directly in Python.

Example with static method
--------------------------

Java::

    package org.test;
    public class Hardware {
        static int getDPI() {
            return metrics.densityDpi;
        }
    }

Python::

    @metaclass(MetaJavaClass)
    class Hardware(JavaClass):
        __javaclass__ = 'org/test/Hardware'
        getDPI = JavaStaticMethod('()I')

    Hardware.getDPI()


Example with instance method
----------------------------

Java::

    package org.test;
    public class Action {
        public String getName() {
            return new String("Hello world")
        }
    }

Python::

    @metaclass(MetaJavaClass)
    class Action(JavaClass):
        __javaclass__ = 'org/test/Action'
        getName = JavaMethod('()Ljava/lang/String;')

    action = Action()
    print(action.getName())
    # will output Hello World


Example with static/instance field
----------------------------------

Java::

    package org.test;
    public class Test {
        public static String field1 = new String("hello");
        public String field2;

        public Test() {
            this.field2 = new String("world");
        }
    }

Python::

    @metaclass(MetaJavaClass)
    class Test(JavaClass):
        __javaclass__ = 'org/test/Test'

        field1 = JavaStaticField('Ljava/lang/String;')
        field2 = JavaField('Ljava/lang/String;')

    # access directly to the static field
    print(Test.field1)

    # create the instance, and access to the instance field
    test = Test()
    print(test.field2)

"""

from ._jclass  import metaclass, java_class  # <AK> jt.jnius additions
from ._jclass  import MetaJavaBase, MetaJavaClass
from ._jclass  import JavaClass, JavaObject, JavaException
from ._jfield  import JavaField,  JavaStaticField
from ._jmethod import JavaMethod, JavaStaticMethod, JavaMultipleMethod
from ._jproxy  import java_implementer  # <AK> jt.jnius addition
from ._jproxy  import PythonJavaClass as _PythonJavaClass, java_method
from ._func    import cast, find_javaclass
from ._jvm     import detach

__all__ = ('metaclass', 'java_class', 'java_implementer', 'java_method',
           'MetaJavaBase', 'MetaJavaClass', 'PythonJavaClass', 'JavaClass',
           'JavaObject', 'JavaException', 'JavaField', 'JavaStaticField',
           'JavaMethod', 'JavaStaticMethod', 'JavaMultipleMethod',
           'cast', 'find_javaclass', 'detach')


@metaclass(MetaJavaBase)
class PythonJavaClass(_PythonJavaClass):

    """Base class to create a java class from python"""

    @java_method("()I", name="hashCode")
    def hashCode(self):

        HASHCODE_MAX = 2 ** 31 - 1
        return id(self) % HASHCODE_MAX

    @java_method("()Ljava/lang/String;", name="hashCode")
    def hashCode_(self):

        return "{}".format(self.hashCode())

    @java_method("()Ljava/lang/String;", name="toString")
    def toString(self):

        return repr(self)

    @java_method("(Ljava/lang/Object;)Z", name="equals")
    def equals(self, other):

        return self.hashCode() == other.hashCode()


del _PythonJavaClass
