# Copyright (c) 2014-2019 Adam Karpierz
# Licensed under the MIT License
# http://opensource.org/licenses/MIT


def start_jvm(jvm):

    from ... import jnius_config as config

    jvmoptions = config.options
    jvmoptions.append("-Djava.class.path={}".format(config.expand_classpath()))
    jvm.start(*jvmoptions, ignoreUnrecognized=False)
    config.vm_running = True


def stop_jvm(jvm):  # <AK> added

    from ... import jnius_config as config

    if config.vm_running:
        jvm.shutdown()
    config.vm_running = False
