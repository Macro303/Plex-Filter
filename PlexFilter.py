#!/usr/bin/env python3
import json
import logging
from pathlib import Path

import yaml
from discord_webhook import DiscordWebhook
from flask import Flask, request, abort
from flask_restx import Api, Resource

TOP_DIR = Path(__file__).resolve().parent

LOGGER = logging.getLogger(__name__)

config_file = TOP_DIR.joinpath('config.yaml')
if config_file.exists():
    with open(config_file, 'r', encoding='UTF-8') as yaml_file:
        CONFIG = yaml.safe_load(yaml_file) or {
            'Discord': None,
            'Ignored Events': []
        }
else:
    config_file.touch()
    CONFIG = {
        'Discord': None,
        'Ignored Events': []
    }
with open(config_file, 'w', encoding='UTF-8') as yaml_file:
    yaml.safe_dump(CONFIG, yaml_file)

app = Flask(__name__)
api = Api(app)


def init_logger() -> None:
    stream_logger = logging.StreamHandler()
    stream_logger.setLevel(logging.INFO)

    log_dir = TOP_DIR.joinpath('logs')
    log_dir.mkdir(exist_ok=True)
    file_logger = logging.FileHandler(filename=log_dir.joinpath('Notifier.log'), encoding='UTF-8')
    file_logger.setLevel(logging.DEBUG)

    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)-8s] {%(name)s} | %(message)s',
        handlers=[
            stream_logger,
            file_logger
        ]
    )


@api.route('/plex', methods=['POST'])
class Plex(Resource):
    def post(self):
        _request = request.form.to_dict(flat=True)
        payload = json.loads(str(_request.get('payload', {})))

        if payload.get('event') in CONFIG['Ignored Events']:
            abort(400, 'Ignored Event')

        content = None

        if payload.get('event') == 'library.on.deck':
            LOGGER.info(f"Library On Deck Event: {payload}")

        elif payload.get('event') == 'library.new':
            LOGGER.debug(f"Library New Event: {payload}")
            content = "Added "
            if payload.get('Metadata', {}).get('type') == 'episode':
                content += f"{payload.get('Metadata', {}).get('grandparentTitle')} - S{payload.get('Metadata', {}).get('parentIndex'):02}E{payload.get('Metadata', {}).get('index'):02} - {payload.get('Metadata', {}).get('title')}"
            elif payload.get('Metadata', {}).get('type') == 'movie':
                content += payload.get('Metadata', {}).get('title')
            else:
                LOGGER.error(f"Un-mapped Media type: `{payload.get('Metadata', {}).get('type')}`")
                abort(400, f"Un-mapped Media type: `{payload.get('Metadata', {}).get('type')}`")

        elif payload.get('event') == 'media.pause':
            LOGGER.info(f"Media Pause Event: {payload}")

        elif payload.get('event') == 'media.play':
            LOGGER.debug(f"Media Play Event: {payload}")
            content = f"{payload.get('Account', {}).get('title')} is playing "
            if payload.get('Metadata', {}).get('type') == 'episode':
                content += f"{payload.get('Metadata', {}).get('grandparentTitle')} - S{payload.get('Metadata', {}).get('parentIndex'):02}E{payload.get('Metadata', {}).get('index'):02} - {payload.get('Metadata', {}).get('title')}"
            elif payload.get('Metadata', {}).get('type') == 'movie':
                content += payload.get('Metadata', {}).get('title')
            else:
                LOGGER.error(f"Un-mapped Media type: `{payload.get('Metadata', {}).get('type')}`")
                abort(400, f"Un-mapped Media type: `{payload.get('Metadata', {}).get('type')}`")

        elif payload.get('event') == 'media.rate':
            LOGGER.info(f"Media Rate Event: {payload}")

        elif payload.get('event') == 'media.resume':
            LOGGER.info(f"Media Resume Event: {payload}")

        elif payload.get('event') == 'media.scrobble':
            LOGGER.debug(f"Media Scrobble Event: {payload}")
            content = f"{payload.get('Account', {}).get('title')} scrobbled "
            if payload.get('Metadata', {}).get('type') == 'episode':
                content += f"{payload.get('Metadata', {}).get('grandparentTitle')} - S{payload.get('Metadata', {}).get('parentIndex'):02}E{payload.get('Metadata', {}).get('index'):02} - {payload.get('Metadata', {}).get('title')}"
            elif payload.get('Metadata', {}).get('type') == 'movie':
                content += f"{payload.get('Metadata', {}).get('title')} ({payload.get('Metadata', {}).get('year')})"
            else:
                LOGGER.error(f"Un-mapped Media type: `{payload.get('Metadata', {}).get('type')}`")
                abort(400, f"Un-mapped Media type: `{payload.get('Metadata', {}).get('type')}`")

        elif payload.get('event') == 'media.stop':
            LOGGER.info(f"Media Stop Event: {payload}")

        elif payload.get('event') == 'admin.database.backup':
            LOGGER.debug(f"Admin Database Backup Event: {payload}")
            content = f"Database backup of {payload.get('Server', {}).get('title')}"

        elif payload.get('event') == 'admin.database.corrupted':
            LOGGER.info(f"Admin Database Corrupted Event: {payload}")

        elif payload.get('event') == 'device.new':
            LOGGER.info(f"Device New Event: {payload}")

        elif payload.get('event') == 'playback.started':
            LOGGER.debug(f"Playback Started Event: {payload}")
            content = f"{payload.get('Account', {}).get('title')} started "
            if payload.get('Metadata', {}).get('type') == 'episode':
                content += f"{payload.get('Metadata', {}).get('grandparentTitle')} - S{payload.get('Metadata', {}).get('parentIndex'):02}E{payload.get('Metadata', {}).get('index'):02} - {payload.get('Metadata', {}).get('title')}"
            elif payload.get('Metadata', {}).get('type') == 'movie':
                content += payload.get('Metadata', {}).get('title')
            else:
                LOGGER.error(f"Un-mapped Media type: `{payload.get('Metadata', {}).get('type')}`")
                abort(400, f"Un-mapped Media type: `{payload.get('Metadata', {}).get('type')}`")

        discord_hook = DiscordWebhook(
            url=CONFIG['Discord'],
            username='Plex Notifier',
            content=content or f"`{payload.get('event')}` by {payload.get('Account', {}).get('title')}"
        )
        discord_response = discord_hook.execute()
        LOGGER.info(f"Discord: {discord_response}")

        return {'success': True}


@api.errorhandler
def default_error_handler(error):
    """Default error handler"""
    LOGGER.error('Error Grabbed')
    return {'message': str(error)}, getattr(error, 'code', 500)


if __name__ == '__main__':
    init_logger()
    app.env = 'DEV'
    app.run(port=6795)
