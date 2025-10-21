# Notification Payloads Reference

This document describes the notification formats used by dbot for both webhook and Redis queue delivery.

## Table of Contents

- [Overview](#overview)
- [Notification Types](#notification-types)
- [Webhook Format](#webhook-format)
- [Redis Format](#redis-format)
- [Template Variables](#template-variables)
- [Integration Examples](#integration-examples)

## Overview

dbot sends notifications when users join or leave Discord voice channels. Notifications can be delivered via:

1. **Webhooks** - HTTP GET requests to configured URLs with templated query parameters
2. **Redis Queues** - JSON messages pushed to Redis lists

Each channel can be configured to send notifications to multiple destinations.

## Notification Types

dbot generates four types of notifications:

| Event Type | Trigger | Description |
|------------|---------|-------------|
| `new_user` | User joins channel | Fired when a user joins a voice channel |
| `user_left` | User leaves channel | Fired when a user leaves a voice channel |
| `users_connected` | First user(s) join empty channel | Fired when users connect to an empty channel |
| `users_left` | Last user leaves channel | Fired when the last user leaves, making the channel empty |

## Webhook Format

Webhooks are delivered as HTTP GET requests. The URL is constructed using Jinja2 templates with variables replaced at runtime.

### Template Configuration

Configure webhook URLs in your `config.json`:

```json
{
  "channels": [
    {
      "channel_id": 1234567890,
      "webhooks": {
        "new_user_webhooks": ["https://example.com/hook?channel={{id}}&user={{username}}"],
        "user_left_webhooks": ["https://example.com/hook?channel={{id}}&user={{username}}"],
        "users_connected_webhooks": ["https://example.com/hook?channel={{id}}&users={{usernames_safe}}"],
        "users_left_webhooks": ["https://example.com/hook?channel={{id}}"]
      }
    }
  ]
}
```

### Example Webhook Calls

#### new_user Event

**Template:**
```
https://hook.integromat.com/webhook_id?channel_id={{id}}&event={{type}}&username={{username}}&user_id={{user_id}}
```

**Actual Request:**
```
GET https://hook.integromat.com/webhook_id?channel_id=1234567890&event=new_user&username=JohnDoe&user_id=987654321
```

#### user_left Event

**Template:**
```
https://hooks.zapier.com/catch/123456/?ch={{id}}&type={{type}}&user={{username}}&uid={{user_id}}
```

**Actual Request:**
```
GET https://hooks.zapier.com/catch/123456/?ch=1234567890&type=user_left&user=JaneDoe&uid=111222333
```

#### users_connected Event

**Template:**
```
https://example.com/webhook?channel={{id}}&event={{type}}&usernames={{usernames_safe}}
```

**Actual Request:**
```
GET https://example.com/webhook?channel=1234567890&event=users_connected&usernames=Alice%2CBob%2CCharlie
```

Note: `{{usernames_safe}}` is URL-encoded. The example above shows "Alice,Bob,Charlie" encoded.

#### users_left Event

**Template:**
```
https://example.com/webhook?channel={{id}}&event={{type}}
```

**Actual Request:**
```
GET https://example.com/webhook?channel=1234567890&event=users_left
```

## Redis Format

Redis notifications are JSON messages pushed to configured queues using `RPUSH`.

### Message Schema

All Redis messages follow this schema:

```json
{
  "version": 1,
  "type": "new_user|user_left|users_connected|users_left",
  "channel_id": 1234567890,
  "happened_at": "2024-01-15T10:30:45.123456+00:00",
  "data": {
    // Event-specific data
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `version` | integer | Message format version (currently 1) |
| `type` | string | Event type (enum) |
| `channel_id` | integer | Discord channel ID |
| `happened_at` | string | ISO 8601 timestamp with timezone |
| `data` | object | Event-specific payload |

### Event-Specific Data

#### new_user Event

```json
{
  "version": 1,
  "type": "new_user",
  "channel_id": 1234567890,
  "happened_at": "2024-01-15T10:30:45.123456+00:00",
  "data": {
    "id": 987654321,
    "username": "JohnDoe"
  }
}
```

**Data Fields:**
- `id` (integer): Discord user ID
- `username` (string): Discord username

#### user_left Event

```json
{
  "version": 1,
  "type": "user_left",
  "channel_id": 1234567890,
  "happened_at": "2024-01-15T10:35:20.789012+00:00",
  "data": {
    "id": 987654321,
    "username": "JohnDoe"
  }
}
```

**Data Fields:**
- `id` (integer): Discord user ID
- `username` (string): Discord username

#### users_connected Event

```json
{
  "version": 1,
  "type": "users_connected",
  "channel_id": 1234567890,
  "happened_at": "2024-01-15T10:40:10.456789+00:00",
  "data": {
    "usernames": ["Alice", "Bob", "Charlie"],
    "users": [
      {"id": 111111111, "username": "Alice"},
      {"id": 222222222, "username": "Bob"},
      {"id": 333333333, "username": "Charlie"}
    ]
  }
}
```

**Data Fields:**
- `usernames` (array of strings): List of usernames
- `users` (array of objects): Full user information
  - `id` (integer): Discord user ID
  - `username` (string): Discord username

#### users_left Event

```json
{
  "version": 1,
  "type": "users_left",
  "channel_id": 1234567890,
  "happened_at": "2024-01-15T11:00:00.000000+00:00",
  "data": {}
}
```

**Data Fields:** Empty object (no additional data needed)

## Template Variables

### Available Variables by Event Type

#### new_user & user_left

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{{id}}` | integer | Channel ID | `1234567890` |
| `{{type}}` | string | Event type | `new_user` |
| `{{username}}` | string | Discord username | `JohnDoe` |
| `{{user_id}}` | integer | Discord user ID | `987654321` |

#### users_connected

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{{id}}` | integer | Channel ID | `1234567890` |
| `{{type}}` | string | Event type | `users_connected` |
| `{{usernames_safe}}` | string | URL-encoded comma-separated usernames | `Alice%2CBob` |

#### users_left

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{{id}}` | integer | Channel ID | `1234567890` |
| `{{type}}` | string | Event type | `users_left` |

### Variable Encoding

- `{{usernames_safe}}`: Automatically URL-encoded using `urllib.parse.quote_plus()`
- All other string variables: Use raw values (not URL-encoded)
- Tip: If you need other encoded variables, encode them server-side after receiving the webhook

## Integration Examples

### Make.com (formerly Integromat)

```json
{
  "webhooks": {
    "new_user_webhooks": [
      "https://hook.integromat.com/YOUR_WEBHOOK_ID?channel={{id}}&event={{type}}&user={{username}}&uid={{user_id}}"
    ]
  }
}
```

Make will receive the data as query parameters that you can parse and use in your scenario.

### Zapier

```json
{
  "webhooks": {
    "new_user_webhooks": [
      "https://hooks.zapier.com/hooks/catch/123456/abcdef/?channel_id={{id}}&username={{username}}&user_id={{user_id}}"
    ]
  }
}
```

Zapier will parse the query parameters automatically and make them available as trigger data.

### Discord Webhook

```json
{
  "webhooks": {
    "new_user_webhooks": [
      "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN?content=User%20{{username}}%20joined%20channel%20{{id}}"
    ]
  }
}
```

Note: Discord webhooks have specific requirements. You may need a proxy service to transform dbot's GET requests into proper Discord webhook POST requests.

### Redis Consumer (Python)

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

while True:
    # Blocking pop from the queue
    _, message = r.blpop('dbot.events', timeout=0)

    # Parse the message
    event = json.loads(message)

    # Handle different event types
    if event['type'] == 'new_user':
        username = event['data']['username']
        channel = event['channel_id']
        print(f"User {username} joined channel {channel}")

    elif event['type'] == 'users_connected':
        users = event['data']['usernames']
        print(f"Channel became active with users: {', '.join(users)}")
```

### Redis Consumer (Node.js)

```javascript
const redis = require('redis');
const client = redis.createClient();

async function consumeEvents() {
  await client.connect();

  while (true) {
    const message = await client.blPop('dbot.events', 0);
    const event = JSON.parse(message.element);

    switch (event.type) {
      case 'new_user':
        console.log(`${event.data.username} joined channel ${event.channel_id}`);
        break;
      case 'user_left':
        console.log(`${event.data.username} left channel ${event.channel_id}`);
        break;
      case 'users_connected':
        console.log(`Channel ${event.channel_id} active: ${event.data.usernames.join(', ')}`);
        break;
      case 'users_left':
        console.log(`Channel ${event.channel_id} is now empty`);
        break;
    }
  }
}

consumeEvents();
```

## Retry Behavior

### Webhooks

- Automatic retry with exponential backoff (3 attempts)
- Wait time: Random exponential between 0.5s and 60s
- Failures are logged and reported to Sentry (if configured)
- Non-200 responses are treated as failures

### Redis

- No automatic retry (at-least-once delivery guaranteed by Redis)
- Connection failures will cause the bot to crash and restart
- Messages remain in queue until consumed
- Use Redis persistence (RDB/AOF) for durability

## Troubleshooting

### Webhooks Not Firing

1. Check webhook URL is correctly templated in config
2. Verify the remote endpoint is accessible
3. Check bot logs for retry attempts and errors
4. Test the webhook URL manually with curl

### Redis Messages Not Appearing

1. Verify Redis connection URL is correct
2. Check Redis queue name matches in config
3. Confirm Redis is running and accessible
4. Use Redis CLI: `redis-cli LLEN dbot.events` to check queue length

### Missing Notifications

1. Ensure channel ID is correct (enable Developer Mode in Discord)
2. Verify bot has permission to see the voice channel
3. Check bot logs for channel processing messages
4. Confirm notifications are configured for the desired event types

