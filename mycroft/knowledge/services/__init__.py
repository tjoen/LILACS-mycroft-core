from abc import ABCMeta, abstractmethod

__author__ = 'jarbas'


# add here all methods all backends are expected to implement

class KnowledgeBackend():
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, config, emitter):
        pass

    @abstractmethod
    def adquire(self):
        pass

    @abstractmethod
    def emit_node_info(self, info):
        pass

    @abstractmethod
    def stop(self):
        pass
