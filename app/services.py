# coding: utf-8
import datetime
import logging
import typing

from dao import ChannelInfo, ChannelInfoDAO
from models import (
    ChannelActivityNotification,
    ChannelConfig,
    Notification,
    User,
    UserActivityInfo,
)
from sender import CallbackService

logger = logging.getLogger("debug")


class ActivityProcessingService:

    ACTIVITY_LIFETIME = 60 * 60  # 1 hour
    CHANNEL_ACTIVITY_LIFETIME = 60 * 60

    def __init__(
        self,
        channel_info_dao: ChannelInfoDAO,
        callback_service: CallbackService,
        channel_configs: typing.List[ChannelConfig],
    ) -> None:

        self.discord_client = None
        self.channel_info_dao = channel_info_dao
        self.callback_service = callback_service
        self.channel_configs = channel_configs

    def register_client(self, discord_client):
        self.discord_client = discord_client

    async def process(self):
        logger.debug("start processing")
        for channel in self.channel_configs:
            logger.debug(f"extracting users from {channel.channel_id}")
            users = self.discord_client.get_channel_members(channel.channel_id)

            logger.debug(f"{channel.channel_id}: users: {users}")
            activities = []
            channel_info = await self.channel_info_dao.get_channel_info(
                channel_id=channel.channel_id
            )
            if channel_info is not None:
                activities = channel_info.activities

            logger.debug(f"{channel.channel_id}: info - {channel_info}")

            notifications = self._get_user_activity_notifications(users, activities)
            for notification in notifications:
                await self.callback_service.send_user_activity_notification(
                    notification, channel.channel_id
                )

            logger.debug(
                f"{channel.channel_id}: user activity notifications - {notifications}"
            )

            channel_notification = self._get_channel_new_activity_notifications(
                users, channel_info
            )
            if channel_notification:
                await self.callback_service.send_channel_activity_notification(
                    channel_notification, channel.channel_id
                )

            logger.debug(
                f"{channel.channel_id}: channel activity - {channel_notification} "
            )

            activities = self._get_current_user_activity_info(users)
            new_channel_info = ChannelInfo(
                channel_id=channel.channel_id,
                timestamp=int(datetime.datetime.now().timestamp()),
                activities=activities,
            )

            await self.channel_info_dao.write_channel_info(
                channel_info=new_channel_info
            )

    def _get_current_user_activity_info(
        self, users: typing.List[User]
    ) -> typing.List[UserActivityInfo]:
        fresh_activities = []
        processing_timestamp = self._get_processing_timestamp()

        for user in users:
            fresh_activities.append(
                UserActivityInfo(id=user.id, last_seen_timestamp=processing_timestamp)
            )

        return fresh_activities

    def _get_user_activity_notifications(
        self, users: typing.List[User], activity_info: typing.List[UserActivityInfo]
    ) -> typing.List[Notification]:
        processing_timestamp = self._get_processing_timestamp()
        users_by_id = {user.id: user for user in users}
        activity_by_id = {activity.id: activity for activity in activity_info}

        notifications = []
        for user_id in users_by_id.keys():
            user = users_by_id[user_id]
            # new user in chat
            if user_id not in activity_by_id:
                notifications.append(Notification(user=user))
                continue

            # activity outdated
            activity = activity_by_id[user_id]
            if (
                processing_timestamp - activity.last_seen_timestamp
            ) > self.ACTIVITY_LIFETIME:
                notifications.append(Notification(user=user))
                continue

        return notifications

    def _get_channel_new_activity_notifications(
        self,
        users: typing.List[User],
        channel_info: typing.Optional[ChannelInfo],
    ) -> typing.Optional[ChannelActivityNotification]:
        if not channel_info:
            return None

        processing_timestamp = self._get_processing_timestamp()

        if (
            processing_timestamp - channel_info.timestamp
        ) > self.CHANNEL_ACTIVITY_LIFETIME:
            return None

        if not channel_info.activities and users:
            return ChannelActivityNotification(
                channel_id=channel_info.channel_id, users=users
            )

        return None

    def _get_processing_timestamp(self):
        return int(datetime.datetime.now().timestamp())
