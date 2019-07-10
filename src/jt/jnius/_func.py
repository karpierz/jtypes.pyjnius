# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ..jvm.lib.compat import *
from ..jvm.lib import annotate, Union
from ..jvm.lib import public

from ._jclass import JavaClass, JavaException


@public
@annotate(obj=JavaClass)
def cast(destclass, obj):

    from ._conversion import str_types
    from .reflect     import autoclass

    if isinstance(destclass, str_types):
        destclass = autoclass(destclass)

    jobj = destclass(noinstance=True)
    jobj._instantiate_from(obj.j_self, own=False)
    return jobj


@public
@annotate(name=Union[builtins.str, str])
def find_javaclass(name):

    from ._jvm    import JVM
    from .reflect import Class

    jvm = JVM.jvm

    try:
        jclass = jvm.JClass.forName(name)
    except:
        raise JavaException("Class not found {!r}".format(name))

    jc = Class(noinstance=True)
    jc._instantiate_from(jclass)
    return jc
