# vmware-idle-snapshot-notifier

Simple Python script to connect to a vCenter/ESXi system and check any existing VMs for idle snapshots that are older than `n` days. If there are any matches it will send out a notification (to almost any platform wether its Rocket.Chat, Slack, Mattermost, Microsoft Teams, Telegram, E-Mail or HTTP) to a configurable recipient.

## Installation

1. Make sure you've installed all requirements
2. Clone this repository:

    ```shell
    git clone https://github.com/frdmn/vmware-idle-snapshot-notifier
    cd vmware-idle-snapshot-notifier
    ```

3. Install the project using `pip`:

    ```shell
    pip install -r requirements.txt
    ```

4. Copy and adjust the default configuration file:

    ```shell
    cp config.json.sample config.json
    vi config.json
    ```

## Usage / Arguments

```
$ python snapshots.py -h
usage: snapshots.py [-h] [--min-age-in-days MIN_AGE_IN_DAYS] [--config CONFIG]
                    [--debug]

Report idle VMware snapshots

optional arguments:
  -h, --help            show this help message and exit
  --min-age-in-days MIN_AGE_IN_DAYS
                        The minimum age in days of snapshots to report
  --config CONFIG       Path to configuration file
  --debug               Enable debug mode (optional)
```

### Notification configuration

Below you can find a few ([apprise](https://github.com/caronc/apprise#popular-notification-services)) configuration examples:

#### Rocket.Chat

```
"rockets://ADmrL3CmetjNcBbn3/r8RKc9m4gcaS5xMwLf3NfnPArDPJBrLQMbqM7hyParFYP7t8@rocketchat.iwelt.de/?avatar=No"
```

#### E-Mail

```
mailtos://userid:password@server.com?smtp=smtp.server.com
```

## Contributing

1. Fork it
2. Create your feature branch:

    ```shell
    git checkout -b feature/my-new-feature
    ```

3. Commit your changes:

    ```shell
    git commit -am 'Add some feature'
    ```

4. Push to the branch:

    ```shell
    git push origin feature/my-new-feature
    ```

5. Submit a pull request

## Requirements / Dependencies

* Python 2/3
* vCenter credentials

## Version

1.0.0

## License

[MIT](LICENSE)
