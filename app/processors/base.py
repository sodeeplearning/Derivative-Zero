from abc import ABC, abstractmethod


class BaseAbstractProcessor(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...
