# dbot - Discord Voice Channel Activity Monitor

![Build status](https://github.com/astoliarov/dbot/actions/workflows/main.yml/badge.svg)

**dbot** is a service that tracks users in voice channels and sends events when they join or leave.
This service is ready for integration with NoCode automation platforms (Make/Integromat, Zappier & so on) through webhooks mechanism

## Key Features:
- **Real-time Monitoring**: dbot keeps track of who's in and out of voice channels instantly.
- **Notification Options**: It sends notifications through webhooks or via Redis queue when users join or leave, keeping server admins updated.

## Supported events
- User joins a voice channel
- User leaves a voice channel
- User connected to empty channel
- Last user left channel

## Configuration
dbot is configured through environment variables + notification config json file

Env variables (described in src/dbot/infrastructure/config.py):
```
DBOT_DISCORD_TOKEN=<your discord token here>
DBOT_MONITOR_CONFIG_PATH=<path to notifications config file>
DBOT_SENTRY_DSN=<sentry dsn>
DBOT_REDIS_URL=<redis host, For example: redis://localhost:6379>
DBOT_lOGGING_LEVEL=INFO
DBOT_MONITORING_HEALTHCHEKSIO_WEBHOOK=<healthchecks.io webhook>
```
Monitoring config example:
```json
{
  "channels": [
    {
      "channel_id": 10000000000001,
      "webhooks": {
        "users_connected_webhooks": [
          "https://hook.integromat.com/<integromat_hook_id>?channel_id={{id}}&event={{type}}&usernames={{usernames_safe}}"
        ],
        "new_user_webhooks": [
           "https://hook.integromat.com/<integromat_hook_id>?channel_id={{id}}&event={{type}}&un={{username}}&uid={{user_id}}"
        ],
        "users_left_webhooks": [
          "https://hook.integromat.com/<integromat_hook_id>?channel_id={{id}}&event={{type}}"
        ],
        "user_left_webhooks": [
          "https://hook.integromat.com/<integromat_hook_id>?channel_id={{id}}&event={{type}}&un={{username}}&uid={{user_id}}"
        ]
      },
      "redis": {
        "queue": "dbot.events"
      }
    }
  ]
}
```
In this example each event sent both to webhooks and redis queue. You can set both redis and webhooks per channel or only one of them.

