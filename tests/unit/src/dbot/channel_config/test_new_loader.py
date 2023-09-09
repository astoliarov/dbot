import json

from dbot.channel_config.new_loader import JSONLoader
from dbot.model.config import (
    ChannelMonitorConfig,
    MonitorConfig,
    RedisTargetConfig,
    WebhooksTargetConfig,
)


def test__channel_config_loader__empty_config():
    loader = JSONLoader()

    data = {
        "channels": [],
    }

    config = loader.from_string(json.dumps(data))

    assert config == MonitorConfig(channels=[])


def test__channel_config_loader__two_targets():
    loader = JSONLoader()

    data = {
        "channels": [
            {
                "channel_id": 1,
                "webhooks": {
                    "new_user_webhooks": ["http://localhost:8000"],
                    "users_connected_webhooks": ["http://localhost:8001"],
                    "users_leave_webhooks": ["http://localhost:8002"],
                },
                "redis": {
                    "queue": "test_queue",
                },
            }
        ],
    }

    config = loader.from_string(json.dumps(data))

    assert config == MonitorConfig(
        channels=[
            ChannelMonitorConfig(
                channel_id=1,
                webhooks=WebhooksTargetConfig(
                    new_user_webhooks=["http://localhost:8000"],
                    users_connected_webhooks=["http://localhost:8001"],
                    users_leave_webhooks=["http://localhost:8002"],
                ),
                redis=RedisTargetConfig(
                    queue="test_queue",
                ),
            ),
        ]
    )
