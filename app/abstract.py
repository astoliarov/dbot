import typing
from abc import ABC, abstractmethod

from app.model import User


class IDiscordClient(ABC):
    @abstractmethod
    def get_channel_members(self, channel_id: int) -> typing.Optional[list[User]]:
        ...
