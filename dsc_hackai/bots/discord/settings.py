import pathlib
import os
import sys

from dotenv import load_dotenv
from logging.config import dictConfig
import logging

load_dotenv()

DISCORD_API_SECRET = os.getenv('DISCORD_TOKEN')
DISCORD_BOT_CHAT_ID = int(os.getenv('DISCORD_BOT_CHAT_ID'))

BASE_DIR = pathlib.Path(__file__).parent

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {
            "format": "%(levelname)-10s - %(name)-15s : %(message)s"
        }
    },
    "handlers": {
        "console": {
            'level': "DEBUG",
            'class': "logging.StreamHandler",
            'formatter': "verbose",
            'stream': sys.stdout
        },
        "console2": {
            'level': "WARNING",
            'class': "logging.StreamHandler",
            'formatter': "standard"
        },
        "file": {
            'level': "INFO",
            'class': "logging.FileHandler",
            'filename': "logs/infos.log",
            'mode': "w",
            'formatter': "verbose"
        },
    },
    "loggers": {
        "bot": {
            'handlers': ['console'],
            "level": "INFO",
            "propagate": False
        },
        "discord": {
            'handlers': ['console2', "file"],
            "level": "INFO",
            "propagate": False
        }
    }
}

dictConfig(LOGGING_CONFIG)

user_schema = {
    "type": "object",
    "properties": {
        "user_id": {"type": "integer"},
        "state": {
            "type": "string",
        },
        "videos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "process_id": {"type": "string"},
                    "stage": {"type": "string"},
                    "bullet_points": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["title", "process_id"]
            }
        },
        "allowed_to_use": {"type": "boolean"}
    },
    "required": ["user_id"]
}

video_scheme = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "process_id": {"type": "string"},
        "stage": {"type": "string"},
        "bullet_points": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["title", "process_id"]
}


def get_logger(name="bot"):
    return logging.getLogger(name)
