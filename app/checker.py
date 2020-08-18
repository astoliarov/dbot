# coding: utf-8
import datetime
import typing

from dao import ChannelInfoDAO, ChannelInfo
from models import User, UserActivityInfo, Notification


class VoiceChannelChecker:
    CHANNELS_TO_CHECK = [
        740097329318854662
    ]

    def __init__(self, channel_info_dao: ChannelInfoDAO):
        self.discord_client = None
        self.channel_info_dao = channel_info_dao

    def register_client(self, discord_client):
        self.discord_client = discord_client

    async def process(self):
        for channel_id in self.CHANNELS_TO_CHECK:
            users = self.discord_client.get_channel_members(channel_id)

            activities = []
            channel_info = await self.channel_info_dao.get_channel_info(channel_id=channel_id)
            if channel_info is not None:
                activities = channel_info.activities

            print(users)
            print(channel_info)

            _, activities = self._process_channel(users, activities)

            new_channel_info = ChannelInfo(
                channel_id=channel_id,
                timestamp=int(datetime.datetime.now().timestamp()),
                activities=activities,
            )

            await self.channel_info_dao.write_channel_info(channel_info=new_channel_info)

    def _process_channel(
        self,
        users: typing.List[User],
        activity_info: typing.List[UserActivityInfo]
    ) -> typing.Union[typing.List[None], typing.List[UserActivityInfo]]:
        now = int(datetime.datetime.now().timestamp())
        users_by_id = {user.id: user for user in users}
        activity_by_id = {activity.id: activity for activity in activity_info}

        notifications = []
        fresh_activities = []
        for user_id in users_by_id.keys():
            user = users_by_id[user_id]
            # new user in chat
            if user_id not in activity_by_id:
                notifications.append(Notification(user=user))
                continue

            # activity outdated
            activity = activity_by_id[user_id]
            if (now - activity.last_seen_timestamp) > 60 * 60:
                notifications.append(Notification(user=user))
                continue
            else:
                fresh_activities.append(activity)

        fresh_activities_ids = {activity.id for activity in fresh_activities}
        for user in users:
            if user.id in fresh_activities_ids:
                continue

            fresh_activities.append(
                UserActivityInfo(
                    id=user.id,
                    last_seen_timestamp=now
                )
            )

        return notifications, fresh_activities
