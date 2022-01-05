from serializers import ConfigSchema


def test__ConfigSchema__channel_config_loaded__channel_id_parsed_correctly():

    channels_config = {
        "channels": [
            {
                "channel_id": 132132131,
                "channel_activity_postbacks": ["http://0.0.0.0:8000/?id={{user_id}}&username={{username}}"],
            }
        ],
    }

    serializer = ConfigSchema()
    loaded = serializer.load(channels_config)

    assert len(loaded.channels) == 1

    channel = loaded.channels[0]
    assert channel.channel_id == 132132131


def test__ConfigSchema__channel_config_loaded__postback_parsed_correctly():

    channels_config = {
        "channels": [
            {
                "channel_id": 740097329318854662,
                "channel_activity_postbacks": ["http://0.0.0.0:8000/?id={{user_id}}&username={{username}}"],
            }
        ],
    }

    serializer = ConfigSchema()
    loaded = serializer.load(channels_config)
    channel = loaded.channels[0]

    postback = channel.channel_activity_postbacks[0]
    assert len(channel.channel_activity_postbacks) == 1
    assert postback == "http://0.0.0.0:8000/?id={{user_id}}&username={{username}}"
