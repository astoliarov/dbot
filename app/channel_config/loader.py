from models import ChannelsConfig
from serializers import ConfigSerializer


class JSONLoader:
    def from_file(self, path: str) -> ChannelsConfig:
        with open(path, "r") as f:
            raw = f.read()

        serializer = ConfigSerializer.parse_raw(raw)

        return serializer.to_model()
