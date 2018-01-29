from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import unittest
from jt.jnius import JavaClass, MetaJavaClass, JavaMethod
from six import with_metaclass
from jt.jnius import metaclass, java_class     #<AK> for additions for jt.jnius
from jt.jnius import JavaField, JavaException  #<AK> for additions for jt.jnius

class HelloWorldTest(unittest.TestCase):

    def test_helloworld(self):

        class HelloWorld(with_metaclass(MetaJavaClass, JavaClass)):
            __javaclass__ = 'org/jnius/HelloWorld'
            hello = JavaMethod('()Ljava/lang/String;')

        a = HelloWorld()
        self.assertEqual(a.hello(), 'world')

    #<AK> additions for jt.jnius

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

    #</AK>
