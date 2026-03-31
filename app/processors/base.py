from abc import ABC, abstractmethod

import config


class BaseAbstractProcessor(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...
