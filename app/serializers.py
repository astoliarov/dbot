# coding: utf-8

from marshmallow import Schema, fields, validate, ValidationError


class UserActivityInfoSchema(Schema):
    id = fields.Int()
    last_seen_timestamp = fields.Int()


class ChannelInfoSchema(Schema):
    channel_id = fields.Int()
    timestamp = fields.Int()
    activities = fields.List(fields.Nested(UserActivityInfoSchema))
