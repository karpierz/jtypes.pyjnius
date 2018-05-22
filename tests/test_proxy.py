from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# from six.moves import range  #<AK> unnecessary
import unittest  #<AK> for additions for jt.jnius
import sys
if sys.version_info.major >= 3: long = int

from jt.jnius import autoclass, java_method, PythonJavaClass, cast
from jt.jnius import JavaException  #<AK> for additions for jt.jnius
# from nose.tools import *  #<AK> unnecessary

print('1: declare a TestImplem that implement Collection')


class TestImplemIterator(PythonJavaClass):
    __javainterfaces__ = [
        #'java/util/Iterator',
        'java/util/ListIterator', ]

    def __init__(self, collection, index=0):
        self.collection = collection
        self.index = index

    @java_method('()Z')
    def hasNext(self):
        return self.index < len(self.collection.data)

    @java_method('()Ljava/lang/Object;')
    def next(self):
        obj = self.collection.data[self.index]
        self.index += 1
        return obj

    @java_method('()Z')
    def hasPrevious(self):
        return self.index >= 0

    @java_method('()Ljava/lang/Object;')
    def previous(self):
        self.index -= 1
        obj = self.collection.data[self.index]
        return obj

    @java_method('()I')
    def previousIndex(self):
        return self.index - 1

    @java_method('()Ljava/lang/String;')
    def toString(self):
        return repr(self)

    @java_method('(I)Ljava/lang/Object;')
    def get(self, index):
        return self.collection.data[index - 1]

    @java_method('(Ljava/lang/Object;)V')
    def set(self, obj):
        self.collection.data[self.index - 1] = obj


class TestImplem(PythonJavaClass):
    __javainterfaces__ = ['java/util/List']

    def __init__(self, *args):
        super(TestImplem, self).__init__(*args)
        self.data = list(args)

    @java_method('()Ljava/util/Iterator;')
    def iterator(self):
        it = TestImplemIterator(self)
        return it

    @java_method('()Ljava/lang/String;')
    def toString(self):
        return repr(self)

    @java_method('()I')
    def size(self):
        return len(self.data)

    @java_method('(I)Ljava/lang/Object;')
    def get(self, index):
        return self.data[index]

    @java_method('(ILjava/lang/Object;)Ljava/lang/Object;')
    def set(self, index, obj):
        old_object = self.data[index]
        self.data[index] = obj
        return old_object

    @java_method('()[Ljava/lang/Object;')
    def toArray(self):
        return self.data

    @java_method('()Ljava/util/ListIterator;')
    def listIterator(self):
        it = TestImplemIterator(self)
        return it

    @java_method('(I)Ljava/util/ListIterator;',
                         name='ListIterator')
    def listIteratorI(self, index):
        it = TestImplemIterator(self, index)
        return it


class TestBadSignature(PythonJavaClass):
    __javainterfaces__ = ['java/util/List']

    @java_method('(Landroid/bluetooth/BluetoothDevice;IB[])V')
    def bad_signature(self, *args):
        pass


#<AK> additions for jt.jnius
class TestBadInterface(PythonJavaClass):
    __javainterfaces__ = ['java/nonexistent/List']


#<AK> makes a module-level code as unittests (ProxyTest)
class ProxyTest(unittest.TestCase):

    def test_proxies(self):

        Short = autoclass('java.lang.Short')
        Float = autoclass('java.lang.Float')

        #<AK> extends tests for different types (not only for ints as in original)
        for coll in (list(map(lambda x: bool(x % 2), range(10))),
                    #list(map(Short, range(10))),
                     list(map(int,   range(10))),
                     list(map(long,  range(10))),
                    #list(map(Float, range(10))),
                     list(map(float, range(10))),
                     list(map(lambda x: chr(ord("A") + x), range(10)))):

            print("1: instantiate the class '{}', with some data of '{}'".format(
                  TestImplem.__name__, type(coll[0])))
            a = TestImplem(*coll)
            print(a)
            print(dir(a))

            print('tries to get a ListIterator')
            iterator = a.listIterator()
            print('iterator is', iterator)
            while iterator.hasNext():
                idx  = iterator.index
                elem = iterator.next()
                print('at index', idx, 'value is', elem)
                self.assertEqual(elem, coll[idx])

            print('3: Do cast to a collection')
            a2 = cast('java.util.Collection', a.j_self)
            print(a2)

            print('4: Try few method on the collection')
            Collections = autoclass('java.util.Collections')
            #print(Collections.enumeration(a))

            ret = Collections.max(a)
            print('Collections.max():', ret)
            self.assertEqual(ret, max(coll))

            print('Order of data before Collections.reverse():', a.data)
            Collections.reverse(a)
            print('Order of data after  Collections.reverse():', a.data)
            coll = list(reversed(coll))
            self.assertEqual(a.data, coll)

            print('Order of data before Collections.swap(2,3):', a.data)
            Collections.swap(a, 2, 3)
            print('Order of data after  Collections.swap(2,3):', a.data)
            coll[2], coll[3] = coll[3], coll[2]
            self.assertEqual(a.data, coll)

            print('Order of data before Collections.rotate(5):', a.data)
            Collections.rotate(a, 5)
            print('Order of data after  Collections.rotate(5):', a.data)
            coll = coll[-5:] + coll[:-5]
            self.assertEqual(a.data, coll)

            print('Order of data before shuffle():', a.data)
            Collections.shuffle(a)
            print('Order of data after shuffle():', a.data)

            # XXX We have issues for methosd with multiple signature
            ret = Collections.max(a2)
            print('-> Collections.max():', ret)
            self.assertEqual(ret, max(coll))

    def test_bad_signature(self):
        # test bad signature
        threw = False
        try:
            TestBadSignature()
        except Exception:
            threw = True

        if not threw:
            raise Exception("Failed to throw for bad signature")

    #<AK> additions for jt.jnius
    def test_bad_interface(self):
        # test bad interface
        threw = False
        try:
            TestBadInterface()
        except JavaException:
            threw = True

        if not threw:
            raise Exception("Failed to throw for bad interface")
