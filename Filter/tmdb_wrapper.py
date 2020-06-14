#!/usr/bin/env python3
import logging
import re
from typing import Optional, Dict, Any

import requests

LOGGER = logging.getLogger(__name__)

API_URL = 'https://api.themoviedb.org/3'
IMAGE_URL = 'https://image.tmdb.org/t/p/w500'
WEB_URL = 'https://www.themoviedb.org'
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Plex Filter"
}


class Movie:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['title']
        self.description = data['overview']
        self.release_date = data['release_date']
        self.image_path = data['poster_path']

    def get_image_url(self) -> Optional[str]:
        if self.image_path:
            return IMAGE_URL + self.image_path
        return None

    def get_web_url(self) -> str:
        return f"{WEB_URL}/movie/{self.id}-{self.name.replace(' ', '-')}"


class TvShow:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['overview']
        self.image_path = data['poster_path']

    def get_image_url(self) -> Optional[str]:
        if self.image_path:
            return IMAGE_URL + self.image_path
        return None

    def get_web_url(self) -> str:
        return f"{WEB_URL}/tv/{self.id}-{self.name.replace(' ', '-')}"


def hide_url(url: str) -> str:
    items = re.match(r"^.+api_key=(.*?)&.+$", url)
    return url.replace(items[1], "<HIDDEN>")


def request_json(url: str, headers: Optional[Dict[str, str]] = None, timeout=100) -> Optional[Dict[str, Any]]:
    if headers is None:
        headers = HEADERS
    try:
        LOGGER.debug(f"GET: >>> - {url} - {headers}")
        response = requests.get(url, headers=headers, timeout=timeout)
        status_code = response.status_code
        response.raise_for_status()
        if response.status_code == 200:
            result = response.json()
            LOGGER.info(f"GET: {status_code} - {url}")
            return result
    except requests.exceptions.HTTPError as err:
        LOGGER.error(err)
    except TypeError as err:
        LOGGER.error(err)
    return None


def search_movie(tmdb_key: Optional[str], movie) -> Optional[Movie]:
    if not tmdb_key:
        return None
    url = f"{API_URL}/search/movie?api_key={tmdb_key}&query={movie.media_title}&year={movie.year}"
    response = request_json(url=url)
    LOGGER.debug(f"Movie Search Response: {response}")
    if response and response['results']:
        return Movie(response['results'][0])
    return None


def search_episode(tmdb_key: Optional[str], episode) -> Optional[TvShow]:
    if not tmdb_key:
        return None
    url = f"{API_URL}/search/tv?api_key={tmdb_key}&query={episode.show_title}"
    response = request_json(url=url)
    LOGGER.debug(f"Tv Show Search Response: {response}")
    if response and response['results']:
        return TvShow(response['results'][0])
    return None


def search_tv_show(tmdb_key: Optional[str], show) -> Optional[TvShow]:
    if not tmdb_key:
        return None
    url = f"{API_URL}/search/tv?api_key={tmdb_key}&query={show.media_title}"
    response = request_json(url=url)
    LOGGER.debug(f"Tv Show Search Response: {response}")
    if response and response['results']:
        return TvShow(response['results'][0])
    return None
