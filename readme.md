# dbot - Discord Voice Channel Activity Monitor

![Build status](https://github.com/astoliarov/dbot/actions/workflows/main.yml/badge.svg)
![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

**dbot** is a production-ready Discord bot that monitors voice channel activity and sends real-time notifications when users join or leave. Perfect for community managers, automation enthusiasts, and anyone who needs to track voice channel usage.

## Table of Contents

- [Key Features](#key-features)
- [Supported Events](#supported-events)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Monitoring & Observability](#monitoring--observability)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Key Features

- **Real-time Monitoring**: Tracks voice channel activity with configurable polling intervals
- **Flexible Notifications**: Send events via webhooks (Make.com, Zapier, etc.) or Redis queues
- **Multi-Channel Support**: Monitor multiple voice channels with independent configurations
- **Template-Based Webhooks**: Customize webhook URLs with dynamic data using Jinja2 templates
- **Production Ready**: Comprehensive monitoring, structured logging, error tracking, and health checks
- **Scalable Architecture**: Clean separation of concerns, async/await, type-safe Python 3.12+
- **NoCode Integration**: Direct integration with Make.com, Zapier, n8n, and other automation platforms

## Supported Events

| Event | Trigger | Use Case |
|-------|---------|----------|
| **User Joins** (`new_user`) | Individual joins channel | Welcome messages, logging, analytics |
| **User Leaves** (`user_left`) | Individual leaves channel | Goodbye messages, session tracking |
| **Channel Activated** (`users_connected`) | First user(s) join empty channel | Start recording, enable bots |
| **Channel Empty** (`users_left`) | Last user leaves | Stop recording, cleanup resources |

## Architecture Overview

```
┌─────────────────┐
│  Discord API    │
│  (Voice Events) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│           Discord Client (Polling)              │
│  - Monitors voice channels every 10 seconds    │
│  - Fetches current channel members              │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│      Activity Processing Service                │
│  - Compares current vs previous state           │
│  - Generates notifications                      │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│           Repository (Redis)                    │
│  - Stores previous channel state                │
│  - TTL: 1 hour                                  │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│        Notification Router                      │
│  - Routes events to configured destinations     │
└────────┬───────────────────────────┬────────────┘
         │                           │
         ▼                           ▼
┌──────────────────┐      ┌──────────────────────┐
│ Webhooks         │      │  Redis Queues        │
│ Connector        │      │  Connector           │
│ - HTTP GET       │      │  - RPUSH messages    │
│ - Retry logic    │      │  - JSON payloads     │
│ - Jinja2 temps   │      │  - Multiple queues   │
└──────────────────┘      └──────────────────────┘
```

### Core Components

- **Discord Client**: Polls Discord API for voice channel member lists
- **Repository**: Redis-backed state storage with automatic expiration
- **Notification Router**: Distributes events to configured connectors (Strategy pattern)
- **Connectors**: Pluggable delivery mechanisms (Webhooks, Redis queues)
- **Instrumentation**: Prometheus metrics, structured logging, Sentry error tracking

## Prerequisites

### Required

- **Python 3.12.1+**: Modern async/await features and type hints
- **Redis**: State storage and message queue
- **Discord Bot Token**: Create at [Discord Developer Portal](https://discord.com/developers/applications)

### Optional

- **Docker & Docker Compose**: For containerized deployment
- **Kubernetes + Helm**: For production orchestration
- **Sentry Account**: Error tracking and monitoring
- **Healthchecks.io**: Uptime monitoring

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token (you'll need this for `DBOT_DISCORD_TOKEN`)
5. Enable "Server Members Intent" and "Presence Intent" under "Privileged Gateway Intents"
6. Invite the bot to your server with permissions:
   - View Channels
   - Connect (for voice channels)
7. Enable "Developer Mode" in Discord (User Settings → Advanced)
8. Right-click voice channel → Copy ID (this is your `channel_id`)

## Installation & Setup

### Local Development

```bash
# Clone the repository
git clone https://github.com/astoliarov/dbot.git
cd dbot

# Install Poetry (dependency manager)
make poetry

# Install dependencies
make install-dev

# Create environment configuration
cp .env.example .env
# Edit .env with your settings

# Create notification configuration
cp config.example.json config.json
# Edit config.json with your channel IDs and webhook URLs

# Start Redis (using Docker)
make local-deploy/infrastructure/up

# Run the bot
make run/app
```

### Using Docker

```bash
# Build the Docker image
make docker/build

# Start infrastructure (Redis)
make local-deploy/infrastructure/up

# Start the application
make local-deploy/application/up
```

## Configuration

Configuration is split between environment variables (infrastructure) and JSON file (channels/notifications).

### Environment Variables

See [`.env.example`](.env.example) for all available options.

**Required:**
```bash
DBOT_DISCORD_TOKEN=your_bot_token_here
DBOT_REDIS_URL=redis://localhost:6379
```

**Optional but Recommended:**
```bash
DBOT_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
DBOT_LOGGING_LEVEL=INFO
DBOT_MONITORING_HEALTHCHECKSIO_WEBHOOK=https://hc-ping.com/your-uuid
```

### Channel Configuration

Create a JSON file (default: `./src/dbot/config_loader/config.json`) defining which channels to monitor and where to send notifications.

See [`config.example.json`](config.example.json) for detailed examples.

**Basic Example:**
```json
{
  "channels": [
    {
      "channel_id": 1234567890123456789,
      "webhooks": {
        "new_user_webhooks": [
          "https://hook.integromat.com/abc123?channel={{id}}&user={{username}}&uid={{user_id}}"
        ],
        "user_left_webhooks": [
          "https://hook.integromat.com/abc123?channel={{id}}&user={{username}}&uid={{user_id}}"
        ],
        "users_connected_webhooks": [
          "https://hook.integromat.com/abc123?channel={{id}}&users={{usernames_safe}}"
        ],
        "users_left_webhooks": [
          "https://hook.integromat.com/abc123?channel={{id}}"
        ]
      },
      "redis": {
        "queue": "dbot.events"
      }
    }
  ]
}
```

### Template Variables

Webhook URLs support Jinja2 templating:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{id}}` | Channel ID | `1234567890` |
| `{{type}}` | Event type | `new_user` |
| `{{username}}` | Discord username | `JohnDoe` |
| `{{user_id}}` | Discord user ID | `987654321` |
| `{{usernames_safe}}` | URL-encoded comma-separated usernames | `Alice%2CBob` |

**Full documentation:** [PAYLOADS.md](PAYLOADS.md)

## Deployment

### Docker

```bash
# Build
docker build -t dbot:latest .

# Run
docker run -d \
  --name dbot \
  --env-file .env \
  -v $(pwd)/config.json:/app/config.json \
  dbot:latest
```

### Docker Compose

```bash
# Start infrastructure + app
make local-deploy/application/up

# View logs
docker-compose logs -f dbot

# Stop
make local-deploy/application/down
```

### Kubernetes with Helm

```bash
# Install
helm install dbot ./helm/dbot \
  --set discord_token=YOUR_TOKEN \
  --set redis_url=redis://redis-service:6379 \
  --set-file dbot_config=./config.json

# Upgrade
helm upgrade dbot ./helm/dbot \
  --set discord_token=YOUR_TOKEN \
  --set-file dbot_config=./config.json

# Uninstall
helm uninstall dbot
```

**Production Checklist:**
- [ ] Set `DBOT_SENTRY_DSN` for error tracking
- [ ] Configure `DBOT_MONITORING_HEALTHCHECKSIO_WEBHOOK` for uptime monitoring
- [ ] Set `DBOT_LOGGING_LEVEL=WARNING` or `ERROR` in production
- [ ] Use Redis with persistence (RDB or AOF)
- [ ] Set resource limits in Kubernetes
- [ ] Configure Prometheus scraping for metrics endpoint (port 3333)
- [ ] Set up alerts for failed webhook deliveries

## Monitoring & Observability

### Prometheus Metrics

Metrics exposed on `http://localhost:3333/metrics`:

| Metric | Type | Description |
|--------|------|-------------|
| `channel_processing` | Summary | Time to process a single channel |
| `channels_processing` | Summary | Time to process all channels |
| `notifications` | Counter | Total notifications generated |
| `notifications_processing` | Summary | Time to send notifications |
| `webhooks` | Counter | Total webhook calls made |
| `redis_events` | Counter | Total Redis messages published |

### Structured Logging

All logs use structured format (JSON-ready):

```python
logger.info("channel_processing.started", channel_id=123, user_count=5)
```

**Log Levels:**
- `DEBUG`: Detailed flow information
- `INFO`: Normal operations, channel processing
- `WARNING`: Degraded performance, retries
- `ERROR`: Failed operations, exceptions

### Health Checks

- **Healthchecks.io**: Bot pings configured URL after each successful processing cycle
- **Kubernetes Liveness**: Check if process is running
- **Prometheus**: Monitor metrics for anomalies

### Error Tracking

Sentry integration captures:
- Unhandled exceptions
- Webhook delivery failures
- Discord API errors
- Redis connection issues

## Development

### Running Tests

```bash
# Unit tests
make test/unit

# Integration tests (requires infrastructure)
make local-deploy/infrastructure/up
make test/integration

# All tests
make test
```

### Code Quality

```bash
# Format code
make fmt

# Run linters
make lint

# Individual linters
make lint/black
make lint/isort
make lint/flake8
make lint/mypy
```

### Project Structure

```
dbot/
├── src/dbot/
│   ├── main.py                 # Application entry point
│   ├── services.py             # Core business logic
│   ├── repository.py           # Redis state management
│   ├── connectors/             # Notification delivery
│   │   ├── router.py           # Event routing
│   │   ├── webhooks/           # HTTP webhook delivery
│   │   └── rqueue/             # Redis queue delivery
│   ├── dscrd/                  # Discord client wrapper
│   ├── model/                  # Domain models
│   ├── config_loader/          # JSON configuration
│   └── infrastructure/         # Logging, monitoring, config
├── tests/
│   ├── unit/                   # Fast, isolated tests
│   └── integration/            # Tests with real dependencies
├── helm/                       # Kubernetes deployment
└── .github/workflows/          # CI/CD pipelines
```

## Troubleshooting

### Bot Not Starting

**Issue**: Bot crashes on startup

**Solutions:**
- Check Redis is running: `redis-cli ping`
- Verify Discord token is valid
- Check all environment variables are set
- Review logs for specific error

### No Notifications Received

**Issue**: Events happening but no webhooks/messages

**Solutions:**
1. Check channel ID is correct (Discord Developer Mode → Copy ID)
2. Verify bot has permission to see voice channel
3. Test webhook URL manually with curl
4. Check Redis queue: `redis-cli LLEN dbot.events`
5. Review bot logs for notification generation

### Webhook Failures

**Issue**: Webhooks timing out or failing

**Solutions:**
- Check webhook endpoint is accessible
- Review Sentry for error details
- Verify template variables are correct
- Check webhook provider (Make.com, Zapier) is working
- Reduce webhook count if hitting rate limits

### High Memory Usage

**Issue**: Bot consuming too much memory

**Solutions:**
- Reduce number of monitored channels
- Decrease polling frequency (adjust `check_interval` in code)
- Check for Redis connection leaks
- Monitor with Prometheus metrics

### Discord API Rate Limits

**Issue**: Bot being rate-limited by Discord

**Solutions:**
- Increase `check_interval` (default: 10 seconds)
- Reduce number of monitored channels per instance
- Discord allows ~50 req/s, so max ~500 channels per instance at 10s interval
- Deploy multiple instances with separate bot tokens for more channels

## API Reference

For detailed notification formats, webhook templates, and Redis message schemas, see:

**[PAYLOADS.md](PAYLOADS.md)** - Complete notification reference with examples

### Quick Reference

**Event Types:**
- `new_user` - Individual joins channel
- `user_left` - Individual leaves channel
- `users_connected` - First user(s) join empty channel
- `users_left` - Last user leaves channel

**Delivery Methods:**
- Webhooks (HTTP GET with templated URLs)
- Redis queues (JSON messages via RPUSH)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters (`make test lint`)
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

**Development Guidelines:**
- Follow existing code style (Black, isort)
- Add tests for new features
- Update documentation
- Use type hints throughout
- Keep functions focused and small

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

---

**Need Help?** Open an issue on [GitHub](https://github.com/astoliarov/dbot/issues)

**Want to Contribute?** Pull requests are welcome!
