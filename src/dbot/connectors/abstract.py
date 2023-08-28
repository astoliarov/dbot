from abc import ABC, abstractmethod
from functools import singledispatchmethod

from dbot.model.notifications import Notification


class IConnector(ABC):
    @abstractmethod
    @singledispatchmethod
    async def send(self, notification: Notification) -> None:
        ...
