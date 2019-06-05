# vsphere-idle-snapshot-notifier

Simple Python script to connect to a vCenter/ESXi system and check any existing VMs for idle snapshots that are older than `n` days. If there are any matches it will send out a notification (currently only by mail) to a configurable mail recipient.

## Installation

1. Make sure you've installed all requirements
2. Clone this repository:

    ```shell
    git clone https://github.com/frdmn/vsphere-idle-snapshot-notifier
    ```

3. Install the project using `pip`:

    ```shell
    pip install -r requirements.txt
    ```

4. Copy and adjust the default configuration file:

    ```shell
    cp config.json.sample config.json
    ```

## Usage

```
$ python snapshot.py
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
* vCenter credentialss

## Version

1.0.0

## License

[MIT](LICENSE)
