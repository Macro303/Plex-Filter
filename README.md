<img src="https://raw.githubusercontent.com/Macro303/Plex-Filter/main/logo.png" align="left" width="120" height="120" alt="Plex Filter Logo">

# Plex Filter
[![Version](https://img.shields.io/github/tag-pre/Macro303/Plex-Filter.svg?label=version&style=flat-square)](https://github.com/Macro303/Plex-Filter/releases)
[![Issues](https://img.shields.io/github/issues/Macro303/Plex-Filter.svg?style=flat-square)](https://github.com/Macro303/Plex-Filter/issues)
[![Contributors](https://img.shields.io/github/contributors/Macro303/Plex-Filter.svg?style=flat-square)](https://github.com/Macro303/Plex-Filter/graphs/contributors)
[![License](https://img.shields.io/github/license/Macro303/Plex-Filter.svg?style=flat-square)](https://opensource.org/licenses/MIT)

Simple Webhook listener to filter Webhooks from Plex before sending them to Discord

## Built Using
 - Python 3.8.2
 - PyYAML 5.3.1
 - discord_webhook 0.8.0
 - flask 1.1.2
 - pytz 2020.1
 - requests 2.24.0

## Execution
1. Create a Plex Webhook to `http://localhost:6795/plex`
2. Run the following:
    ```bash
    $ pip install -r requirements.txt
    $ python -m Filter
    ```
3. Stop the script
4. Edit the created `config.yaml` with your Discord Webhook, any events to be ignored and your [TMDB API v3 Key](https://developers.themoviedb.org/3)
4. Run the following:
    ```bash
   $ python -m Filter
    ```

## Notes
The current known events are:
 - library.on.deck
 - library.new
 - media.pause
 - media.play
 - media.rate
 - media.resume
 - media.scrobble
 - media.stop
 - admin.database.backup
 - admin.database.corrupted
 - device.new
 - playback.started

## Socials
[![Discord | The Playground](https://discord.com/api/v6/guilds/618581423070117932/widget.png?style=banner2)](https://discord.gg/nqGMeGg)