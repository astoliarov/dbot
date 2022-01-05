# coding: utf-8

from marshmallow import Schema, fields, post_load
from models import ChannelConfig, ChannelsConfig


class UserActivityInfoSchema(Schema):
    id = fields.Int()
    last_seen_timestamp = fields.Int()


class ChannelInfoSchema(Schema):
    channel_id = fields.Int()
    timestamp = fields.Int()
    activities = fields.List(fields.Nested(UserActivityInfoSchema))


class ChannelConfigSchema(Schema):
    channel_id = fields.Int()
    user_activity_postbacks = fields.List(fields.Str())
    channel_activity_postbacks = fields.List(fields.Str())

    @post_load
    def load_channel_config(self, data, **kwargs):
        if "channel_activity_postbacks" not in data:
            data["channel_activity_postbacks"] = []

        if "user_activity_postbacks" not in data:
            data["user_activity_postbacks"] = []

        return ChannelConfig(**data)


class ConfigSchema(Schema):
    channels = fields.List(fields.Nested(ChannelConfigSchema))

    @post_load
    def load_config(self, data, **kwargs):
        return ChannelsConfig(**data)
