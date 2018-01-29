# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ..jvm.lib.compat import *
from ..jvm.lib import annotate, Union
from ..jvm.lib import public

from ._jclass import JavaClass, JavaException


@public
@annotate(obj=JavaClass)
def cast(destclass, obj):

    from .reflect import autoclass

    if isinstance(destclass, (builtins.str, str)):
        destclass = autoclass(destclass)

    jobj = destclass(noinstance=True)
    jobj._instantiate_from(obj.j_self, borrowed=True)
    return jobj


@public
@annotate(name=Union[builtins.str, str])
def find_javaclass(name):

    from ._jvm    import get_jvm
    from .reflect import Class

    jvm = get_jvm()

    try:
        jclass = jvm.JClass.forName(name)
    except:
        raise JavaException("Class not found {!r}".format(name))

    jc = Class(noinstance=True)
    jc._instantiate_from(jclass)
    return jc
