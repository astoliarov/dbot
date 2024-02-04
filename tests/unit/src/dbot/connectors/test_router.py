from unittest.mock import AsyncMock

from dbot.connectors.router import NotificationRouter
from dbot.model import MonitorConfig, User
from dbot.model.config import (
    ChannelMonitorConfig,
    RedisTargetConfig,
    TargetTypeEnum,
    WebhooksTargetConfig,
)
from dbot.model.notifications import NewUserInChannelNotification


async def test__NotificationRouter__send__event_and_config_has_2_targets__sent_to_both():
    config = MonitorConfig(
        channels=[
            ChannelMonitorConfig(
                channel_id=1,
                redis_queues=[
                    RedisTargetConfig(
                        queue="test_queue",
                    ),
                ],
                webhooks=WebhooksTargetConfig(
                    new_user_webhooks=["http://localhost:8000"],
                    users_connected_webhooks=["http://localhost:8001"],
                    users_left_webhooks=["http://localhost:8002"],
                    user_left_webhooks=["http://localhost:8003"],
                ),
            )
        ]
    )
    router = NotificationRouter(
        configs=config,
    )

    redis_connector_mock = AsyncMock()
    webhooks_connector_mock = AsyncMock()

    router.register_connector(TargetTypeEnum.REDIS, redis_connector_mock)
    router.register_connector(TargetTypeEnum.WEBHOOKS, webhooks_connector_mock)

    notification = NewUserInChannelNotification(
        user=User(
            username="test",
            id=1,
        ),
        channel_id=1,
    )
    notifications = [notification]

    await router.send(notifications)

    redis_connector_mock.send.assert_called_once_with(notifications)
    webhooks_connector_mock.send.assert_called_once_with(notifications)


async def test__NotificationRouter__send__event_and_config_has_only_webhooks__sent_to_webhooks():
    config = MonitorConfig(
        channels=[
            ChannelMonitorConfig(
                channel_id=1,
                redis_queues=None,
                webhooks=WebhooksTargetConfig(
                    new_user_webhooks=["http://localhost:8000"],
                    users_connected_webhooks=["http://localhost:8001"],
                    users_left_webhooks=["http://localhost:8002"],
                    user_left_webhooks=["http://localhost:8003"],
                ),
            )
        ]
    )
    router = NotificationRouter(
        configs=config,
    )

    redis_connector_mock = AsyncMock()
    webhooks_connector_mock = AsyncMock()

    router.register_connector(TargetTypeEnum.REDIS, redis_connector_mock)
    router.register_connector(TargetTypeEnum.WEBHOOKS, webhooks_connector_mock)

    notification = NewUserInChannelNotification(
        user=User(
            username="test",
            id=1,
        ),
        channel_id=1,
    )
    notifications = [notification]

    await router.send(notifications)

    redis_connector_mock.send.assert_not_called()
    webhooks_connector_mock.send.assert_called_once_with(notifications)


async def test__NotificationRouter__send__event_and_config_has_only_redis__sent_to_redis():
    config = MonitorConfig(
        channels=[
            ChannelMonitorConfig(
                channel_id=1,
                redis_queues=[
                    RedisTargetConfig(
                        queue="test_queue",
                    ),
                ],
                webhooks=None,
            )
        ]
    )
    router = NotificationRouter(
        configs=config,
    )

    redis_connector_mock = AsyncMock()
    webhooks_connector_mock = AsyncMock()

    router.register_connector(TargetTypeEnum.REDIS, redis_connector_mock)
    router.register_connector(TargetTypeEnum.WEBHOOKS, webhooks_connector_mock)

    notification = NewUserInChannelNotification(
        user=User(
            username="test",
            id=1,
        ),
        channel_id=1,
    )
    notifications = [notification]

    await router.send(notifications)

    redis_connector_mock.send.assert_called_once_with(notifications)
    webhooks_connector_mock.send.assert_not_called()


async def test__NotificationRouter__send__event_and_config_has_2_redis_queues__sent_to_redis_once():
    config = MonitorConfig(
        channels=[
            ChannelMonitorConfig(
                channel_id=1,
                redis_queues=[
                    RedisTargetConfig(
                        queue="test_queue",
                    ),
                    RedisTargetConfig(
                        queue="second_queue",
                    ),
                ],
                webhooks=None,
            )
        ]
    )
    router = NotificationRouter(
        configs=config,
    )

    redis_connector_mock = AsyncMock()
    webhooks_connector_mock = AsyncMock()

    router.register_connector(TargetTypeEnum.REDIS, redis_connector_mock)
    router.register_connector(TargetTypeEnum.WEBHOOKS, webhooks_connector_mock)

    notification = NewUserInChannelNotification(
        user=User(
            username="test",
            id=1,
        ),
        channel_id=1,
    )
    notifications = [notification]

    await router.send(notifications)

    redis_connector_mock.send.assert_called_once_with(notifications)
