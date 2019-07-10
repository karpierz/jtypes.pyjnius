# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import absolute_import

import collections as abcoll

from ...jvm.lib.compat import *
from ...jvm.lib.compat import PY2
from ...jvm.lib import annotate
from ...jvm.lib import public

from .._constants import EJavaType
from .._constants import EMatchType

from ._base_handler import _ObjectHandler
from ._base_handler import str_types


@public
class ArrayHandler(_ObjectHandler):

    __slots__ = ('_component_thandler',)

    def __init__(self, state, jclass):

        super(ArrayHandler, self).__init__(state, EJavaType.ARRAY, jclass)
        self._component_thandler = None # state.type_manager.get_handler(jclass.getComponentType())

    componentHandler = property(lambda self: self._component_thandler)

    def match(self, val):

        from .._nativetypes import ByteArray
        from .._jclass      import JavaClass

        elem_definition = self._jclass[1:]

        if val is None:
            return EMatchType.PERFECT
        elif elem_definition == "B" and isinstance(val, (bytes, bytearray, ByteArray)):
            return EMatchType.PERFECT
        elif elem_definition == "B" and isinstance(val, str) and PY2:
            return EMatchType.PERFECT
        elif elem_definition == "C" and isinstance(val, str_types):
            return EMatchType.PERFECT
        elif isinstance(val, (list, tuple)):
            # calculate the score for our subarray
            if len(val) > 0:
                # if there are supplemental arguments we compute the score
                thandler = self._jt_jvm.type_manager.get_handler(elem_definition)
                sub_score = EMatchType.PERFECT
                for elem in val:
                    match_level = thandler.match(elem)
                    if match_level == EMatchType.NONE:
                        return EMatchType.NONE
                    sub_score += match_level
                if sub_score != EMatchType.NONE:
                    # the supplemental arguments match the varargs arguments
                    return EMatchType.PERFECT
                else:
                    return EMatchType.NONE
            else:
                # if there is no supplemental arguments it might be the good method but there
                # may be a method with a better signature so we don't change this method score
                return 0
        return EMatchType.NONE

    #@annotate('jt.jvm.JArray')
    def toJava(self, val):

        from .._jvm import JVM

        jenv = JVM.jenv

        jclass = self._jt_jvm.JClass(None, self._jt_jvm._jvm.Object.Class, own=False)

        elem_definition = self._jclass[1:]

        size = len(val)
        jarr = self._jt_jvm.JArray.newObjectArray(size, jclass)
        for idx, elem in enumerate(val):
            item_definition = self.__to_jarray_conversions.get(type(elem), elem_definition)
            elem_thandler = self._jt_jvm.type_manager.get_handler(item_definition)
            jobj = elem_thandler.toJava(elem)
            jenv.SetObjectArrayElement(jarr.handle, idx,
                                       jobj.handle if jobj is not None else None)
        return jarr

    __to_jarray_conversions = {
        bool:  "Z",
        int:   "I",
        long:  "J",
        float: "F",
        str:   "Ljava/lang/String;",
        bytes: "Ljava/lang/String;" if PY2 else "B",
    }

    def toPython(self, val):

        from .._conversion import convert_jarray_to_python
        jarr = val.asArray(own=False) if val is not None else None
        return convert_jarray_to_python(self._jclass, jarr)

    def setInstance(self, fld, this, val):

        elem_definition = self._jclass[1:]

        raise Exception("Invalid field definition '{}'".format(self._jclass[0]))

    def setArgument(self, pdescr, args, pos, val):

        from .._nativetypes import ByteArray
        from .._jclass      import JavaException
        from .._conversion  import convert_python_to_jarray

        elem_definition = self._jclass[1:]

        if val is None:
            val = None
        else:
            if isinstance(val, str_types):
                if PY2 and elem_definition == "B":
                    val = list(ord(ch) for ch in val)
                elif elem_definition == "C":
                    val = list(val)
            if isinstance(val, ByteArray) and elem_definition != "B":
                raise JavaException("Cannot use ByteArray for signature {}".format(self._jclass))
            if not isinstance(val, (list, tuple, ByteArray, bytes, bytearray)):
                raise JavaException("Expecting a python list/tuple, got {!r}".format(val))
            val = convert_python_to_jarray(self._jclass, val)
        args.setArray(pos, val)
