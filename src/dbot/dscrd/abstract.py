from abc import ABC, abstractmethod

from dbot.model import User


class IDiscordClient(ABC):
    @abstractmethod
    def get_channel_members(self, channel_id: int) -> list[User] | None:
        ...
