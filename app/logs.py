from logging import config as logging_config


def initialize_logs(logging_level: str) -> None:
    config = {
        "version": 1,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
            }
        },
        "loggers": {
            "debug": {
                "level": logging_level,
                "handlers": [
                    "console",
                ],
            },
        },
    }
    logging_config.dictConfig(config)
