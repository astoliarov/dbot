from abc import ABC, abstractmethod
from enum import Enum

from dbot.model.notifications import Notification


class NotificationTypesEnum(Enum):
    NEW_USER = "new_user"
    USERS_CONNECTED = "users_connected"
    USERS_LEAVE = "users_leave"


class IConnector(ABC):
    @abstractmethod
    async def send(self, notifications: list[Notification]) -> None:
        ...
