from __future__ import absolute_import
import unittest
from jnius import autoclass

class InheritanceTest(unittest.TestCase):

    def test_newinstance(self):
        Parent = autoclass('org.jnius.Parent')
        Child = autoclass('org.jnius.Child')

        child = Child.newInstance()

        self.assertTrue(isinstance(child, Child))
        self.assertTrue(isinstance(child, Parent))
