# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from ...jvm.lib import platform

if platform.is_android:
    from ._android import start_jvm, stop_jvm
else:
    from ._dlopen  import start_jvm, stop_jvm

del platform
