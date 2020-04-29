<img src="https://raw.githubusercontent.com/Macro303/Plex-Notifier/master/logo.jpg" align="left" width="120" height="120" alt="Plex Notifier Logo">

# Plex Notifier
[![Version](https://img.shields.io/github/tag-pre/Macro303/Plex-Notifier.svg?label=version&style=flat-square)](https://github.com/Macro303/Plex-Notifier/releases)
[![Issues](https://img.shields.io/github/issues/Macro303/Plex-Notifier.svg?style=flat-square)](https://github.com/Macro303/Plex-Notifier/issues)
[![Contributors](https://img.shields.io/github/contributors/Macro303/Plex-Notifier.svg?style=flat-square)](https://github.com/Macro303/Plex-Notifier/graphs/contributors)
[![License](https://img.shields.io/github/license/Macro303/Plex-Notifier.svg?style=flat-square)](https://opensource.org/licenses/MIT)

Simple Webhook listener to filter Webhooks from Plex before sending them to Discord

## Built Using
 - Python 3.8.2
 - PyYAML 5.3.1
 - discord_webhook 0.7.1
 - flask-restx 0.2.0

## Execution
1. Run the following:
    ```bash
    $ pip install -r requirements.txt
    $ python PlexNotifier.py
    ```
2. Stop the script
2. Create a Plex Webhook to `http://localhost:6795/plex`
3. Edit the created `config.yaml` with your Discord Webhook and any events to be ignored.
4. Run the following:
    ```bash
   $ python PlexNotifier.py
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