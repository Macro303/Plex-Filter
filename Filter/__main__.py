#!/usr/bin/env python3
import json
import logging
from datetime import datetime

from discord_webhook import DiscordWebhook, DiscordEmbed
from flask import Flask, request, abort, jsonify

from Filter import CONFIG, parse_payload, rgb_to_int, localize_timestamp, search_movie, search_tv_show, \
    search_episode, Media
from Logger import init_logger

LOGGER = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/plex', methods=['POST'])
def plex_ep():
    _request = request.form.to_dict(flat=True)
    payload = json.loads(str(_request.get('payload', {})))

    LOGGER.debug(f"Plex Webhook: {payload}")

    if payload.get('event') in CONFIG['Ignored Events']:
        abort(400, 'Ignored Event')

    plex_request = parse_payload(payload)
    tmdb = None
    if isinstance(plex_request, Media):
        if plex_request.media_type == 'movie':
            tmdb = search_movie(CONFIG['TMDB API Key'], plex_request)
        elif plex_request.media_type == 'episode':
            tmdb = search_episode(CONFIG['TMDB API Key'], plex_request)
        elif plex_request.media_type == 'show':
            tmdb = search_tv_show(CONFIG['TMDB API Key'], plex_request)

    discord_hook = DiscordWebhook(
        url=CONFIG['Discord'],
        username='Plex Filter',
    )
    discord_embed = DiscordEmbed(
        title=plex_request.get_title(),
        description=plex_request.get_description(),
        color=rgb_to_int(70, 130, 180),
        timestamp=localize_timestamp(datetime.now()),
        url=(tmdb.get_web_url() if tmdb else None)
    )
    discord_embed.set_thumbnail(
        url=(tmdb.get_image_url() if tmdb else None)
    )
    footers = []
    if plex_request.event not in ['library.new', 'admin.database.backup']:
        if plex_request.account_name:
            footers.append(plex_request.account_name)
    if plex_request.server:
        footers.append(plex_request.server)
    if plex_request.device:
        footers.append(plex_request.device)
    discord_embed.set_footer(
        text=' | '.join(footers),
        icon_url=plex_request.account_thumb
    )
    discord_hook.add_embed(discord_embed)

    discord_response = discord_hook.execute()
    LOGGER.debug(f"Discord Request: {discord_hook.json}")
    LOGGER.info(f"Discord Response: [{discord_response.status_code}]{discord_response.content.decode('UTF-8')}")

    return jsonify({'success': True})


if __name__ == '__main__':
    init_logger('Plex-Filter')
    app.env = 'DEV'
    app.run(port=6795)
