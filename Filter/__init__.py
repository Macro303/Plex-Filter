#!/usr/bin/env python3
import logging
from datetime import datetime
from pathlib import Path

import yaml
from pytz import timezone

TOP_DIR = Path(__file__).resolve().parent.parent

LOGGER = logging.getLogger(__name__)

config_file = TOP_DIR.joinpath('config.yaml')
if config_file.exists():
    with open(config_file, 'r', encoding='UTF-8') as yaml_file:
        CONFIG = yaml.safe_load(yaml_file) or {
            'Discord': None,
            'Ignored Events': [],
            'Timezone': 'Pacific/Auckland',
            'TMDB API Key': None
        }
else:
    config_file.touch()
    CONFIG = {
        'Discord': None,
        'Ignored Events': [],
        'Timezone': 'Pacific/Auckland',
        'TMDB API Key': None
    }
with open(config_file, 'w', encoding='UTF-8') as yaml_file:
    yaml.safe_dump(CONFIG, yaml_file)


def rgb_to_int(red: int, green: int, blue: int) -> int:
    return (red << 16) + (green << 8) + blue


def localize_timestamp(timestamp: datetime) -> str:
    return timezone(CONFIG['Timezone']) \
        .localize(timestamp) \
        .astimezone(timezone(CONFIG['Timezone'])) \
        .isoformat(sep='T')
