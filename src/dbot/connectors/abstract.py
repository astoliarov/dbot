from abc import ABC, abstractmethod
from enum import Enum

from dbot.model.notifications import Notification


class NotificationTypesEnum(Enum):
    NEW_USER = "new_user"
    USERS_CONNECTED = "users_connected"
    USERS_LEFT = "users_left"
    USER_LEFT = "user_left"


class IConnector(ABC):
    @abstractmethod
    async def send(self, notifications: list[Notification]) -> None:
        ...
