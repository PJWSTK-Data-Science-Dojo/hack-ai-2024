import pathlib
import os
from dotenv import load_dotenv
from logging.config import dictConfig
import logging

load_dotenv()

DISCORD_API_SECRET = os.getenv('DISCORD_TOKEN')
DISCORD_BOT_CHAT_ID = int(os.getenv('DISCORD_BOT_CHAT_ID'))

BASE_DIR = pathlib.Path(__file__).parent

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # Fixed typo
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
            'formatter': "standard"
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
    "loggers": {  # Fixed typo
        "bot": {
            'handlers': ['console'],
            "level": "INFO",  # Fixed typo
            "propagate": False
        },
        "discord": {
            'handlers': ['console2', "file"],
            "level": "INFO",  # Fixed typo
            "propagate": False
        }
    }
}

dictConfig(LOGGING_CONFIG)


def get_logger(name="bot"):
    return logging.getLogger(name)