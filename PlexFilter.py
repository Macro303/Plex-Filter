#!/usr/bin/env python3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import yaml
from discord_webhook import DiscordWebhook, DiscordEmbed
from flask import Flask, request, abort, jsonify
from pytz import timezone

from Logger import init_logger

TOP_DIR = Path(__file__).resolve().parent

LOGGER = logging.getLogger(__name__)

config_file = TOP_DIR.joinpath('config.yaml')
if config_file.exists():
    with open(config_file, 'r', encoding='UTF-8') as yaml_file:
        CONFIG = yaml.safe_load(yaml_file) or {
            'Discord': None,
            'Ignored Events': [],
            'Timezone': 'Pacific/Auckland'
        }
else:
    config_file.touch()
    CONFIG = {
        'Discord': None,
        'Ignored Events': [],
        'Timezone': 'Pacific/Auckland'
    }
with open(config_file, 'w', encoding='UTF-8') as yaml_file:
    yaml.safe_dump(CONFIG, yaml_file)

app = Flask(__name__)


@app.route('/plex', methods=['POST'])
def plex_ep():
    _request = request.form.to_dict(flat=True)
    payload = json.loads(str(_request.get('payload', {})))

    if payload.get('event') in CONFIG['Ignored Events']:
        abort(400, 'Ignored Event')

    event_name = clean_str(payload.get('event'))
    if payload.get('Metadata', {}).get('type'):
        event_name = event_name.replace('Media', clean_str(payload.get('Metadata', {}).get('type')))
    event_description = None
    event_colour = rgb_to_int(70, 130, 180)

    LOGGER.debug(f"{event_name}: {payload}")

    if payload.get('event') == 'library.on.deck':
        pass
    elif payload.get('event') == 'library.new':
        event_description = f"{parse_metadata(payload.get('Metadata'))} on {payload.get('Server', {}).get('title')}"
    elif payload.get('event') == 'media.pause':
        event_description = f"{parse_metadata(payload.get('Metadata'))} on {payload.get('Player', {}).get('title')}"
    elif payload.get('event') == 'media.play':
        event_description = f"{parse_metadata(payload.get('Metadata'))} on {payload.get('Player', {}).get('title')}"
    elif payload.get('event') == 'media.rate':
        event_description = f"{parse_metadata(payload.get('Metadata'))} on {payload.get('Player', {}).get('title')}"
    elif payload.get('event') == 'media.resume':
        event_description = f"{parse_metadata(payload.get('Metadata'))} on {payload.get('Player', {}).get('title')}"
    elif payload.get('event') == 'media.scrobble':
        event_description = f"{parse_metadata(payload.get('Metadata'))} on {payload.get('Player', {}).get('title')}"
    elif payload.get('event') == 'media.stop':
        event_description = f"{parse_metadata(payload.get('Metadata'))} on {payload.get('Player', {}).get('title')}"
    elif payload.get('event') == 'admin.database.backup':
        event_description = f"{payload.get('Server', {}).get('title')} Server"
    elif payload.get('event') == 'admin.database.corrupted':
        pass
    elif payload.get('event') == 'device.new':
        event_description = f"{payload.get('Player', {}).get('title')} Device"
    elif payload.get('event') == 'playback.started':
        event_description = f"{parse_metadata(payload.get('Metadata'))} on {payload.get('Player', {}).get('title')}"

    discord_hook = DiscordWebhook(
        url=CONFIG['Discord'],
        username='Plex Filter',
    )
    discord_embed = DiscordEmbed(
        title=event_name,
        description=event_description,
        color=event_colour,
        timestamp=localize_timestamp(datetime.now())
    )
    discord_embed.set_footer(text=payload.get('Account', {}).get('title'),
                             icon_url=payload.get('Account', {}).get('thumb'))
    discord_hook.add_embed(discord_embed)

    discord_response = discord_hook.execute()
    LOGGER.debug(f"Discord Request: {discord_hook.json}")
    LOGGER.info(f"Discord Response: [{discord_response.status_code}]{discord_response.content.decode('UTF-8')}")

    return jsonify({'success': True})


def clean_str(text: str) -> str:
    if text:
        return text.replace('.', ' ').title()
    return text


def rgb_to_int(red: int, green: int, blue: int) -> int:
    return (red << 16) + (green << 8) + blue


def parse_metadata(metadata: Dict[str, Any]) -> Optional[str]:
    title = None
    if metadata.get('type') == 'episode':
        title = f"{metadata.get('grandparentTitle')} - S{metadata.get('parentIndex'):02}E{metadata.get('index'):02} - {metadata.get('title')}"
    elif metadata.get('type') == 'movie':
        title = metadata.get('title')
    elif metadata.get('type') == 'clip':
        title = metadata.get('title')
    elif metadata.get('type') == 'show':
        title = metadata.get('title')
    else:
        LOGGER.error(f"Un-mapped Media type: `{metadata.get('type')}`")
        abort(400, f"Un-mapped Media type: `{metadata.get('type')}`")
    return title


def localize_timestamp(timestamp: datetime) -> str:
    return timezone(CONFIG['Timezone']) \
        .localize(timestamp) \
        .astimezone(timezone(CONFIG['Timezone'])) \
        .isoformat(sep='T')


if __name__ == '__main__':
    init_logger('Plex-Filter')
    app.env = 'DEV'
    app.run(port=6795)
