#!/usr/bin/env python3
import json
import logging
from pathlib import Path

import yaml
from discord_webhook import DiscordWebhook, DiscordEmbed
from flask import Flask, request, abort
from flask_restx import Api, Resource

TOP_DIR = Path(__file__).resolve().parent

LOGGER = logging.getLogger(__name__)

config_file = TOP_DIR.joinpath('config.yaml')
if config_file.exists():
    with open(config_file, 'r', encoding='UTF-8') as yaml_file:
        CONFIG = yaml.safe_load(yaml_file) or {
            'Discord': None,
            'Use Embed': True,
            'Ignored Events': []
        }
else:
    config_file.touch()
    CONFIG = {
        'Discord': None,
        'Use Embed': True,
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

        event_name = None
        event_description = None
        event_colour = None
        event_author = None

        content = None

        if payload.get('event') == 'library.on.deck':
            LOGGER.info(f"Library On Deck Event: {payload}")
            event_name = 'library.on.deck'.title()

        elif payload.get('event') == 'library.new':
            LOGGER.debug(f"Library New Event: {payload}")
            event_name = f"New {payload['Metadata']['type']}".title()

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
            event_name = f"{payload['Metadata']['type']} paused".title()

        elif payload.get('event') == 'media.play':
            LOGGER.debug(f"Media Play Event: {payload}")
            event_name = f"{payload['Metadata']['type']} played".title()

            # Plain Message
            content = f"{payload.get('Account', {}).get('title')} is playing "
            if payload.get('Metadata', {}).get('type') == 'episode':
                content += f"{payload.get('Metadata', {}).get('grandparentTitle')} - S{payload.get('Metadata', {}).get('parentIndex'):02}E{payload.get('Metadata', {}).get('index'):02} - {payload.get('Metadata', {}).get('title')}"
            elif payload.get('Metadata', {}).get('type') == 'movie' \
                    or payload.get('Metadata', {}).get('type') == 'clip':
                content += payload.get('Metadata', {}).get('title')
            else:
                LOGGER.error(f"Un-mapped Media type: `{payload.get('Metadata', {}).get('type')}`")
                abort(400, f"Un-mapped Media type: `{payload.get('Metadata', {}).get('type')}`")
            # Embed Message
            embed_title = "Media started"
            embed_colour = get_colour_int_from_rgb(00, 80, 00)

        elif payload.get('event') == 'media.rate':
            LOGGER.info(f"Media Rate Event: {payload}")
            event_name = f"{payload['Metadata']['type']} rated".title()

        elif payload.get('event') == 'media.resume':
            LOGGER.info(f"Media Resume Event: {payload}")
            event_name = f"{payload['Metadata']['type']} resumed".title()

        elif payload.get('event') == 'media.scrobble':
            LOGGER.debug(f"Media Scrobble Event: {payload}")
            event_name = f"{payload['Metadata']['type']} scrobbled".title()

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
            event_name = f"{payload['Metadata']['type']} stopped".title()

        elif payload.get('event') == 'admin.database.backup':
            LOGGER.debug(f"Admin Database Backup Event: {payload}")
            event_name = 'Database backup complete'.title()

            content = f"Database backup of {payload.get('Server', {}).get('title')}"

        elif payload.get('event') == 'admin.database.corrupted':
            LOGGER.info(f"Admin Database Corrupted Event: {payload}")
            event_name = 'Database corrupted'.title()

        elif payload.get('event') == 'device.new':
            LOGGER.debug(f"Device New Event: {payload}")
            event_name = 'New device used'.title()

            content = f"{payload.get('Account', {}).get('title')} has connected with a new device: {payload.get('Player', {}).get('title')}"

        elif payload.get('event') == 'playback.started':
            LOGGER.debug(f"Playback Started Event: {payload}")
            event_name = f"{payload['Metadata']['type']} started".title()

            # Plain Message
            content = f"{payload.get('Account', {}).get('title')} started "
            if payload.get('Metadata', {}).get('type') == 'episode':
                content += f"{payload.get('Metadata', {}).get('grandparentTitle')} - S{payload.get('Metadata', {}).get('parentIndex'):02}E{payload.get('Metadata', {}).get('index'):02} - {payload.get('Metadata', {}).get('title')}"
            elif payload.get('Metadata', {}).get('type') == 'movie':
                content += payload.get('Metadata', {}).get('title')
            else:
                LOGGER.error(f"Un-mapped Media type: `{payload.get('Metadata', {}).get('type')}`")
                abort(400, f"Un-mapped Media type: `{payload.get('Metadata', {}).get('type')}`")
            # Embed Message
            embed_title = "Playback started"
            embed_colour = get_colour_int_from_rgb(00, 80, 00)

        discord_hook = DiscordWebhook(
            url=CONFIG['Discord'],
            username='Plex Filter',
            content=content or f"`{payload.get('event')}` by {payload.get('Account', {}).get('title')}"
        )

        if CONFIG['Use Embed']:
            discord_embed = DiscordEmbed(
                title=event_name,
                description=event_description or content,
                colour=event_colour
            )
            discord_embed.set_footer(name=event_author or payload['Account']['title'])
            discord_hook.add_embed(discord_embed)

        discord_response = discord_hook.execute()
        LOGGER.info(f"Discord: {discord_response}")

        return {'success': True}


@api.errorhandler
def default_error_handler(error):
    """Default error handler"""
    LOGGER.error('Error Grabbed')
    return {'message': str(error)}, getattr(error, 'code', 500)


def get_colour_int_from_rgb(red: int, green: int, blue: int) -> int:
    return (red << 16) + (green << 8) + blue


if __name__ == '__main__':
    init_logger()
    app.env = 'DEV'
    app.run(port=6795)
