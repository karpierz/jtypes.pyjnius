**Currently only as placeholder (because a base package jtypes.jvm is still in development)**

jtypes.pyjnius
==============

Dynamic access to Java classes from Python.

Overview
========

  | **jtypes.pyjnius** is a bridge between Python and Java, allowing these to intercommunicate.
  | It is an effort to allow python programs full access to Java class libraries.

  `PyPI record`_.

  | **jtypes.pyjnius** is a lightweight Python package, based on the *ctypes* or *cffi* library.
  | It is an almost fully compliant implementation of Kivy Team's **PyJNIus** package
    by reimplementing whole its functionality in a clean Python instead of Cython.

About PyJNIus:
--------------

Borrowed from the `original website`_:

  **PyJNIus** is a Python library for accessing Java classes.

  A minimal **PyJNIus** example looks something like this:

  *Quick overview*

  .. --------------

  .. code:: python

     >>> from jnius import autoclass
     >>> System = autoclass('java.lang.System')
     >>> System.out.println('Hello world')
     Hello world

     >>> Stack = autoclass('java.util.Stack')
     >>> stack = Stack()
     >>> stack.push('hello')
     >>> stack.push('world')
     >>> print(stack.pop())
     world
     >>> print(stack.pop())
     hello

Requirements
============

- Either the Sun/Oracle JRE/JDK or OpenJDK.

Installation
============

Prerequisites:

+ Python 2.7 or Python 3.4 or later

  * http://www.python.org/
  * 2.7 and 3.6 are primary test environments.
  * For usage with python-for-android:

    #. Get http://github.com/kivy/python-for-android
    #. Install a distribution

+ pip and setuptools

  * http://pypi.python.org/pypi/pip
  * http://pypi.python.org/pypi/setuptools

To install run::

    python -m pip install --upgrade jtypes.pyjnius

To ensure everything is running correctly you can run the tests using::

    python -m jt.jnius.tests

Development
===========

Visit `development page`_

Installation from sources:

Clone the `sources`_ and run::

    python -m pip install ./jtypes.pyjnius

or on development mode::

    python -m pip install --editable ./jtypes.pyjnius

Prerequisites:

+ Development is strictly based on *tox*. To install it run::

    python -m pip install tox

License
=======

  | Copyright (c) 2014-2018 Adam Karpierz
  |
  | Licensed under the MIT License
  | http://opensource.org/licenses/MIT
  | Please refer to the accompanying LICENSE file.

Authors
=======

* Adam Karpierz <adam@karpierz.net>

.. _PyPI record: https://pypi.python.org/pypi/jtypes.pyjnius
.. _original website: https://pyjnius.readthedocs.io
.. _development page: https://github.com/karpierz/jtypes.pyjnius
.. _sources: https://github.com/karpierz/jtypes.pyjnius
