# Copyright (c) 2014-2018 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT


def start_jvm(jvm):

    from ... import jnius_config as config

    jvmoptions = config.options
    jvmoptions.append("-Djava.class.path={}".format(config.expand_classpath()))
    jvm.start(*jvmoptions, ignoreUnrecognized=False)
    config.vm_running = True
