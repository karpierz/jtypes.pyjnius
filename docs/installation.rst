.. _installation:

Installation
============

*jtypes.pyjnius* depends on `Java <http://www.oracle.com/javase>`_.


Installation on the Desktop
---------------------------

You need the Java JRE or JDK installed (openjdk will do). Then, just type::

    sudo python -m pip install --upgrade jtypes.pyjnius

You can run the tests suite to make sure everything is running right::

    python -m jt.jnius.tests


Installation for Android
------------------------

To use jtypes.pyjnius in an Android app, you must include it in your compiled
Python distribution. You can add it to your requirements explicitly as follows.

If you use `buildozer
<https://buildozer.readthedocs.io/en/latest/>`__, add jtypes.pyjnius to your
requirements in buildozer.spec::

  requirements = jtypes.pyjnius

If you use `python-for-android
<http://python-for-android.readthedocs.io/en/latest/>`__, you just need
to install it as is described here 'Python for android - Getting Started
<https://python-for-android.readthedocs.io/en/latest/quickstart/>'__::

    pip install python-for-android

To test that the installation worked, try::

    p4a recipes

This should return a list of recipes available to be built.

Then, you can use python-for-android directly, by adding jtypes.pyjnius
to the  requirements argument when creating a dist or apk::

    p4a apk --requirements=jtypes.pyjnius

or install jtypes.pyjnius permanently::

    sudo install --upgrade jtypes.pyjnius


Installation for Windows
------------------------

Python and pip must be installed and present in PATH.

1. Download and install JDK and JRE:
    http://www.oracle.com/technetwork/java/javase/downloads/index.html

2. Edit your system and environment variables (use the appropriate Java version):
    Add to Environment Variables:
        * ``JDK_HOME``: C:\\Program Files\\Java\\jdk1.7.0_79\\
        * ``PATH``: C:\\Program Files\\Java\\jdk1.7.0_79\\jre\\bin\\server\\
    Add to System Variables:
        * ``PATH``: C:\\Program Files\\Java\\jdk1.7.0_79\\bin\\`

3. Update pip and setuptools::

    python -m pip install --upgrade pip setuptools

4. Install Pyjnius::

    python -m pip install --upgrade jtypes.pyjnius
