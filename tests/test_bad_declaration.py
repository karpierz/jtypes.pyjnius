from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import unittest
from jnius import JavaException, JavaClass
from jnius.reflect import autoclass

class BadDeclarationTest(unittest.TestCase):

    def test_class_not_found(self):
        # <AK> uncommented because done ok in jt.jnius
        with self.assertRaises(JavaException):  # <AK> changed to use 'with'
            autoclass('org.unknow.class')
        # </AK>
        #with self.assertRaises(JavaException):
        #    autoclass('java/lang/String')

    def test_invalid_attribute(self):
        Stack = autoclass('java.util.Stack')
        with self.assertRaises(AttributeError):  # <AK> changed to use 'with'
            getattr(Stack, 'helloworld')

    def test_invalid_static_call(self):
        Stack = autoclass('java.util.Stack')
        with self.assertRaises(JavaException):  # <AK> changed to use 'with'
            Stack.push('hello')

    def test_with_too_much_arguments(self):
        Stack = autoclass('java.util.Stack')
        stack = Stack()
        with self.assertRaises(JavaException):  # <AK> changed to use 'with'
            stack.push('hello', 'world', 123)

    def test_java_exception_handling(self):
        Stack = autoclass('java.util.Stack')
        stack = Stack()
        with self.assertRaises(JavaException,  # <AK> changed to use 'with'
                               msg="Expected exception to be thrown") as exc:
            stack.pop()
        je = exc.exception
        # print("Got JavaException: " + str(je))
        # print("Got Exception Class: " + je.classname)
        # print("Got stacktrace: \n" + '\n'.join(je.stacktrace))
        self.assertEquals("java.util.EmptyStackException", je.classname)

    def test_java_exception_chaining(self):
        BasicsTest = autoclass('org.jnius.BasicsTest')
        basics = BasicsTest()
        with self.assertRaises(JavaException,  # <AK> changed to use 'with'
                               msg="Expected exception to be thrown") as exc:
            basics.methodExceptionChained()
        je = exc.exception
        # print("Got JavaException: " + str(je))
        # print("Got Exception Class: " + je.classname)
        # print("Got Exception Message: " + je.innermessage)
        # print("Got stacktrace: \n" + '\n'.join(je.stacktrace))
        self.assertEquals("java.lang.IllegalArgumentException", je.classname)
        self.assertEquals("helloworld2", je.innermessage)
        self.assertIn("Caused by:", je.stacktrace)
        self.assertEquals(11, len(je.stacktrace))
