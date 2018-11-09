# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

# on android, rely on SDL to get the JNI env
# cdef extern JNIEnv* SDL_ANDROID_GetJNIEnv()


def start_jvm(jvm):

    # TODO ...
    jvm.__class__.jenv = SDL_ANDROID_GetJNIEnv()[0]


def stop_jvm(jvm):  # <AK> added

    pass
