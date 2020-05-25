#!/usr/bin/env python3
import logging
from typing import Optional

LOGGER = logging.getLogger(__name__)


class Plex:
    def __init__(self, data):
        self.event = data['event']
        self.server = data['Server']['title']
        self.device = data.get('Player', {}).get('title')
        self.account_name = data['Account']['title']
        self.account_thumb = data['Account']['thumb']

    def get_title(self) -> str:
        return self.event.replace('.', ' ').title()

    def get_description(self) -> Optional[str]:
        return None

    def __str__(self) -> str:
        output = 'Plex('
        for key, value in self.__dict__.items():
            output += f"{key}={value}, "
        return output[:-2] + ')'


class Media(Plex):
    def __init__(self, data):
        super(Media, self).__init__(data)
        metadata = data['Metadata']
        self.media_type = metadata['type']
        self.media_title = metadata['title']
        self.summary = metadata['summary']

    def get_title(self) -> str:
        return self.event.replace('media', self.get_media_type()).replace('.', ' ').title()

    def get_description(self) -> str:
        return self.media_title + (f"\n```{self.summary}```" if self.summary else '')

    def get_media_type(self) -> str:
        return self.media_type

    def __str__(self) -> str:
        output = 'Media('
        for key, value in self.__dict__.items():
            output += f"{key}={value}, "
        return output[:-2] + ')'


class Movie(Media):
    def __init__(self, data):
        super(Movie, self).__init__(data)
        metadata = data['Metadata']
        self.year = metadata['year']

    def __str__(self) -> str:
        output = 'Movie('
        for key, value in self.__dict__.items():
            output += f"{key}={value}, "
        return output[:-2] + ')'


class Clip(Media):
    def __init__(self, data):
        super(Clip, self).__init__(data)
        metadata = data['Metadata']
        self.media_subtype = metadata['subtype']

    def get_media_type(self) -> str:
        return self.media_subtype

    def __str__(self) -> str:
        output = 'Clip('
        for key, value in self.__dict__.items():
            output += f"{key}={value}, "
        return output[:-2] + ')'


class Show(Media):
    def __init__(self, data):
        super(Show, self).__init__(data)

    def __str__(self) -> str:
        output = 'Show('
        for key, value in self.__dict__.items():
            output += f"{key}={value}, "
        return output[:-2] + ')'


class Episode(Media):
    def __init__(self, data):
        super(Episode, self).__init__(data)
        metadata = data['Metadata']
        self.show_title = metadata['grandparentTitle']
        self.season_index = metadata['parentIndex']
        self.episode_index = metadata['index']
        self.episode_title = metadata['title']
        self.media_title = f"{self.show_title} - S{self.season_index:02}E{self.episode_index:02} - {self.episode_title}"

    def __str__(self) -> str:
        output = 'Episode('
        for key, value in self.__dict__.items():
            output += f"{key}={value}, "
        return output[:-2] + ')'


def parse_payload(payload) -> Plex:
    if payload['event'] in ['library.new', 'media.pause', 'media.play', 'media.rate', 'media.resume', 'media.scrobble',
                            'media.stop', 'playback.started']:
        if payload['Metadata']['type'] == 'movie':
            return Movie(payload)
        elif payload['Metadata']['type'] == 'clip':
            return Clip(payload)
        elif payload['Metadata']['type'] == 'show':
            return Show(payload)
        elif payload['Metadata']['type'] == 'episode':
            return Episode(payload)
        else:
            LOGGER.warning(f"Unknown Media Type: {payload['Metadata']['Type']} => {payload}")
            return Media(payload)
    elif payload['event'] in ['library.on.deck', 'admin.database.backup', 'admin.database.corrupted', 'device.new']:
        return Plex(payload)
    else:
        LOGGER.error(f"Unknown Plex event: {payload['event']} => {payload}")
        return Plex(payload)
