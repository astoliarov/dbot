# coding: utf-8
import json
import typing

from marshmallow import EXCLUDE
from models import ChannelsConfig
from serializers import ConfigSchema


class JSONLoader:
    def __init__(self):
        self.schema = ConfigSchema(unknown=EXCLUDE)

    def _validate(self, data: typing.Dict[typing.Any, typing.Any]) -> ChannelsConfig:
        return self.schema.load(data)

    def from_file(self, path: str) -> ChannelsConfig:
        with open(path, "r") as f:
            data = json.load(f)

        return self._validate(data)
