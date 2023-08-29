from abc import ABC, abstractmethod
from functools import singledispatchmethod

from dbot.model.notifications import Notification


class IConnector(ABC):
    @singledispatchmethod
    @abstractmethod
    async def send(self, notification: Notification) -> None:
        ...
