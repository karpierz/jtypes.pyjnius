from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import unittest
from jnius import JavaClass, MetaJavaClass, JavaMethod
from jnius import metaclass, java_class     # <AK> for jt.jnius additions
from jnius import JavaField, JavaException  #            -||-
from six import with_metaclass

class HelloWorldTest(unittest.TestCase):

    def test_helloworld(self):

        class HelloWorld(with_metaclass(MetaJavaClass, JavaClass)):
            __javaclass__ = 'org/jnius/HelloWorld'
            hello = JavaMethod('()Ljava/lang/String;')

        a = HelloWorld()
        self.assertEqual(a.hello(), 'world')

    # <AK> additions for jt.jnius

    def test_helloworld1(self):

        @metaclass(MetaJavaClass)
        class HelloWorld(JavaClass):
            __javaclass__ = 'org/jnius/HelloWorld'
            hello = JavaMethod('()Ljava/lang/String;')

        a = HelloWorld()
        self.assertEqual(a.hello(), 'world')

    def test_helloworld2(self):

        @metaclass(MetaJavaClass)
        class HelloWorld(object):
            __javaclass__ = 'org/jnius/HelloWorld'
            hello = JavaMethod('()Ljava/lang/String;')

        a = HelloWorld()
        self.assertEqual(a.hello(), 'world')

    def test_helloworld3(self):

        @java_class()
        class HelloWorld(object):
            __javaclass__ = 'org/jnius/HelloWorld'
            hello = JavaMethod('()Ljava/lang/String;')

        a = HelloWorld()
        self.assertEqual(a.hello(), 'world')

    def test_helloworld4(self):

        @java_class('org/jnius/HelloWorld')
        class HelloWorld(object):
            hello = JavaMethod('()Ljava/lang/String;')

        a = HelloWorld()
        self.assertEqual(a.hello(), 'world')

    def test_bad_field(self):

        @java_class('org/jnius/HelloWorld')
        class HelloWorld(object):
            nonexistent = JavaField('I')

        with self.assertRaises(JavaException) as exc:
            a = HelloWorld()

    # </AK>
