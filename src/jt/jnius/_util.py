# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ..jvm.lib.compat import *
from ..jvm.lib import annotate


@annotate(definition=bytes)
def parse_definition(definition):

    if definition[0] != "(":
        # not a function, just a field
        return definition, None

    # it's a function!
    argdef, d_return = definition[1:].split(")")

    d_args = []
    while len(argdef):

        # read the array char(s)
        prefix = ""
        ch = argdef[0]
        while ch == "[":
            prefix += ch
            argdef = argdef[1:]
            ch = argdef[0]

        if ch in "ZCBSIJFD":

            # native type

            argdef = argdef[1:]
            d_args.append(prefix + ch)

        elif ch == "L":

            # java class

            cname, argdef = argdef.split(";", 1)
            d_args.append(prefix + cname + ";")

        else:
            raise Exception('Invalid "{}" character in definition "{}"'.format(
                            ch, definition))

    return d_return, tuple(d_args)
