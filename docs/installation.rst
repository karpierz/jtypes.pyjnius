.. _installation:

Installation
============

*jtypes.pyjnius* depends on the `Java <http://www.oracle.com/javase>`_
Runtime Environment.


Installation on the Desktop
---------------------------

Python must be installed and present in the ``PATH`` environment variable.

You need the JRE or the JDK installed (openjdk will do). Then, just type::

    sudo python -m pip install --upgrade jtypes.pyjnius

You can run the tests suite to make sure everything is running right::

    python -m jt.jnius.tests  # <AK> FIX it


Installation for Android
------------------------

To use *jtypes.pyjnius* in an Android app, you must include it in your compiled
Python distribution. You can add it to your requirements explicitly as follows.

If you use `buildozer
<https://buildozer.readthedocs.io/en/latest/>`__, add *jtypes.pyjnius* to your
requirements in buildozer.spec::

    requirements = jtypes.pyjnius

If you use `python-for-android
<http://python-for-android.readthedocs.io/en/latest/>`__, you just need
to install it as is described here 'Python for android - Getting Started
<https://python-for-android.readthedocs.io/en/latest/quickstart/>'__::

    python -m pip install python-for-android

To test that the installation worked, try::

    p4a recipes

This should return a list of recipes available to be built.

Then, you can use python-for-android directly, by adding *jtypes.pyjnius*
to the requirements argument when creating a dist or apk::

    p4a apk [...] --requirements=jtypes.pyjnius

or install *jtypes.pyjnius* permanently::

    sudo python -m pip install --upgrade jtypes.pyjnius


Installation for Windows
------------------------

Python must be installed and present in the ``PATH`` environment variable.

1. Download and install the JRE or the JDK:

   http://www.oracle.com/technetwork/java/javase/downloads/index.html

2. Edit your system and environment variables (use the appropriate Java bitness
   and version in the paths):

    Add to your `Environment Variables
    <https://en.wikipedia.org/wiki/Environment_variable>`_:

    * ``JAVA_HOME``: C:\\Program Files\\Java\\jdk1.7.0_79\\bin

3. Update `pip <https://pip.pypa.io/en/stable/installing>`_ and setuptools::

      python -m pip install --upgrade pip setuptools

4. Install *jtypes.pyjnius*::

      python -m pip install --upgrade jtypes.pyjnius


Installation for macOS
----------------------

Python must be installed and present in the ``PATH`` environment variable.

1. Download and install the JRE or the JDK:

   http://www.oracle.com/technetwork/java/javase/downloads/index.html

2. Edit your system and environment variables (use the appropriate Java bitness
   and version in the paths):

    Add to your `Environment Variables
    <https://en.wikipedia.org/wiki/Environment_variable>`_:

    * ``export JAVA_HOME=/usr/libexec/java_home``

3. Update `pip <https://pip.pypa.io/en/stable/installing>`_ and setuptools::

      python -m pip install --upgrade pip setuptools

4. Install *jtypes.pyjnius*::

      python -m pip install --upgrade jtypes.pyjnius
