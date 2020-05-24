<img src="https://raw.githubusercontent.com/Macro303/Plex-Filter/master/logo.png" align="left" width="120" height="120" alt="Plex Filter Logo">

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
 - tmdbsimple 2.2.2

## Execution
1. Run the following:
    ```bash
    $ pip install -r requirements.txt
    $ python PlexFilter.py
    ```
2. Stop the script
2. Create a Plex Webhook to `http://localhost:6795/plex`
3. Edit the created `config.yaml` with your Discord Webhook and any events to be ignored.
4. Run the following:
    ```bash
   $ python PlexFilter.py
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