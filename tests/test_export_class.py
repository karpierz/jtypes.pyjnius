from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import unittest
from jnius import autoclass, java_method, PythonJavaClass
from jnius import java_implementer  # <AK> for jt.jnius additions

Iterable = autoclass('java.lang.Iterable')
ArrayList = autoclass('java.util.ArrayList')
Runnable = autoclass('java.lang.Runnable')
Thread = autoclass('java.lang.Thread')
Object = autoclass('java.lang.Object')

class SampleIterable1(PythonJavaClass):
    __javainterfaces__ = ['java/lang/Iterable']

    @java_method('()Ljava/lang/Iterator;')
    def iterator(self):
        sample = ArrayList()
        sample.add(1)
        sample.add(2)
        return sample.iterator()

# <AK> additions for jt.jnius

@java_implementer()
class SampleIterable2(PythonJavaClass):
    __javainterfaces__ = ['java/lang/Iterable']

    @java_method('()Ljava/lang/Iterator;')
    def iterator(self):
        sample = ArrayList()
        sample.add(1)
        sample.add(2)
        return sample.iterator()

@java_implementer('java/lang/Iterable')
class SampleIterable3(PythonJavaClass):

    @java_method('()Ljava/lang/Iterator;')
    def iterator(self):
        sample = ArrayList()
        sample.add(1)
        sample.add(2)
        return sample.iterator()

_SampleIterables = (SampleIterable1, SampleIterable2, SampleIterable3)

# </AK>

class ExportClassTest(unittest.TestCase):
    def test_is_instance(self):
        array_list = ArrayList()
        thread = Thread()
        for SampleIterable in (_SampleIterables):  # <AK> for jt.jnius additions
            sample_iterable = SampleIterable()

            self.assertIsInstance(sample_iterable, Iterable)
            self.assertIsInstance(sample_iterable, Object)
            self.assertIsInstance(sample_iterable, SampleIterable)
            self.assertNotIsInstance(sample_iterable, Runnable)
            self.assertNotIsInstance(sample_iterable, Thread)

            #self.assertListEqual(sample_iterable.iterator(), [1, 2])

        self.assertIsInstance(array_list, Iterable)
        self.assertIsInstance(array_list, ArrayList)
        self.assertIsInstance(array_list, Object)

        self.assertNotIsInstance(thread, Iterable)
        self.assertIsInstance(thread, Thread)
        self.assertIsInstance(thread, Runnable)

    def test_subclasses_work_for_arg_matching(self):
        for SampleIterable in (_SampleIterables):  # <AK> for jt.jnius additions
            array_list = ArrayList()
            array_list.add(SampleIterable())
            self.assertIsInstance(array_list.get(0), Iterable)
            self.assertIsInstance(array_list.get(0), SampleIterable)

    def assertIsSubclass(self, cls, parent):
        self.assertIs(issubclass(cls, parent), True,  # <AK> chanded to use asserts
                      msg="%s is not a subclass of %s" %
                          (cls.__name__, parent.__name__))

    def assertNotIsSubclass(self, cls, parent):
        self.assertIs(issubclass(cls, parent), False,  # <AK> chanded to use asserts
                      msg="%s is a subclass of %s" %
                      (cls.__name__, parent.__name__))

    def test_is_subclass(self):
        self.assertIsSubclass(Thread, Runnable)
        self.assertIsSubclass(ArrayList, Iterable)
        self.assertIsSubclass(ArrayList, Object)
        for SampleIterable in (_SampleIterables):  # <AK> for jt.jnius additions
            self.assertIsSubclass(SampleIterable, Iterable)
        self.assertNotIsSubclass(Thread, Iterable)
        self.assertNotIsSubclass(ArrayList, Runnable)
        self.assertNotIsSubclass(Runnable, Thread)
        for SampleIterable in (_SampleIterables):  # <AK> for jt.jnius additions
            self.assertNotIsSubclass(Iterable, SampleIterable)
