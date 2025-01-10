# knx2mqtt - A KNX2MQTT Bridge allowing bidirectional telegram transfer

I've created this project as a replacement for the KNX integration of [HomeAssistant](https://home-assistant.io/) that worked not stable in my environment.

It is quite simple and does what it's name says: It works as a bridge between KNX and MQTT translating messages between these in both directions.

## Installation

### Installation using Docker

```
docker run -it --rm --name knx2mqtt -v knx2mqtt.conf:/etc/knx2mqtt.conf docker.io/gbeine/knx2mqtt
```

### Native installation with Python venv

The installation requires at least Python 3.9.
On Raspbian, it is required to install rustc because xknx depends on cryptography which cannot be built without rust.

See [Install Rust](https://www.rust-lang.org/tools/install) for details.

Philosophy is to install it under /usr/local/lib/knx2mqtt and control it via systemd.

```
cd /usr/local/lib
git clone https://github.com/gbeine/knx2mqtt.git
cd knx2mqtt
./install
```

The `install` script creates a virtual python environment using the `venv` module.
All required libraries are installed automatically.
Depending on your system this may take some time.

## Configuration

The configuration is located in `/etc/knx2mqtt.conf`.

Each configuration option is also available as command line argument.

- copy `knx2mqtt.conf.example`
- configure as you like

| option                   | default              | arguments                  | comment                                                                                |
|--------------------------|----------------------|----------------------------|----------------------------------------------------------------------------------------|
| `mqtt_host`              | 'localhost'          | `-m`, `--mqtt_host`        | The hostname of the MQTT server.                                                       |
| `mqtt_port`              | 1883                 | `--mqtt_port`              | The port of the MQTT server.                                                           |
| `mqtt_keepalive`         | 30                   | `--mqtt_keepalive`         | The keep alive interval for the MQTT server connection in seconds.                     |
| `mqtt_clientid`          | 'knx2mqtt'           | `--mqtt_clientid`          | The clientid to send to the MQTT server.                                               |
| `mqtt_user`              | -                    | `-u`, `--mqtt_user`        | The username for the MQTT server connection.                                           |
| `mqtt_password`          | -                    | `-p`, `--mqtt_password`    | The password for the MQTT server connection.                                           |
| `mqtt_topic`             | 'bus/knx'            | `-t`, `--mqtt_topic`       | The topic to publish MQTT message.                                                     |
| `mqtt_tls`               | -                    | `--mqtt_tls`               | Use SSL/TLS encryption for MQTT connection.                                            |
| `mqtt_tls_version`       | 'TLSv1.2'            | `--mqtt_tls_version`       | The TLS version to use for MQTT. One of TLSv1, TLSv1.1, TLSv1.2.                       |
| `mqtt_verify_mode`       | 'CERT_REQUIRED'      | `--mqtt_verify_mode`       | The SSL certificate verification mode. One of CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED. |
| `mqtt_ssl_ca_path`       | -                    | `--mqtt_ssl_ca_path`       | The SSL certificate authority file to verify the MQTT server.                          |
| `mqtt_retain`            | false                |                            | Retain messages published on mqtt                                                      |
| `mqtt_resend_retained`   | false                |                            | Resend retained messages received on mqtt to knx                                       |
| `mqtt_tls_no_verify`     | -                    | `--mqtt_tls_no_verify`     | Do not verify SSL/TLS constraints like hostname.                                       |
| `knx_host`               | 'localhost'          | `--knx_host`               | The address of the KNX tunnel device.                                                  |
| `knx_port`               | 3671                 | `--knx_port`               | The port of the KNX tunnel device.                                                     |
| `knx_local_ip`           | -                    | `--knx_local_ip`           | The ip address of the system that connects to KNX.                                     |
| `knx_individual_address` | -                    | `--knx_individual_address` | The group address of the system that send telegrams to KNX.                            |
| `knx_no_queue`           | -                    | `--knx_no_queue`           | Workaround for scheduling problems of XKNX telegram queue.                             |
| `timestamp`              | -                    | `-z`, `--timestamp`        | Publish timestamps for all topics, e.g. for monitoring purposes.                       |
| `verbose`                | -                    | `-v`, `--verbose`          | Be verbose while running.                                                              |
| -                        | '/etc/knx2mqtt.conf' | `-c`, `--config`           | The path to the config file.                                                           |
| `items`                  | see below            | -                          | The configuration for the items on the KNX bus.                                        |

### KNX

Currently, only KNX tunneling mode is supported.
It may become more in the future, if I found testing environments with according setups.
Feel free to add routing or other options and open a pull request for this.

### Items

Then you can configure your bus topology as items.

Each item need an `address` (the group address) and a `type`.

Optionally you can specify `override_topic`, then the representation on mqtt will not be `1/2/3` (Adress) but the provided topic name.

The default operating mode for an object is to listen on the KNX and publish the telegram values to MQTT.

That may be changed using the following settings:

* `mqtt_subscribe` (default: false): if set to `true`, changes on any related MQTT topic will be processed

```
    ...
    "items": [
        {
            "address": "5/0/10",
            "type": "DPTTemperature",
            "mqtt_subscribe": true
        },
        {
            "address": "5/0/20",
            "type": "DPTHumidity"
        },
        {
            "override_topic": "use/this/on/mqtt",
            "address": "5/0/29",
            "type": "DPTHumidity"
        },
        ...
    ]
    ...
```

Unfortunately, the list of types is not part of the xknx documentation.
But the examples in the file I provide with the project may fit for the most purposes.
All supported types can be found in the [xknx sources](https://github.com/XKNX/xknx/blob/main/xknx/dpt/__init__.py).



### Publishing

All values are published using the group address and the MQTT topic.

So, the Date exposing sensor in the example is listening for `bus/knx/0/0/1` and the switch is listening on and publishing to `bus/knx/0/1/1`.

## Running knx2mqtt

I use [systemd](https://systemd.io/) to manage my local services.

## Support

I have not the time (yet) to provide professional support for this project.
But feel free to submit issues and PRs, I'll check for it and honor your contributions.

## License

The whole project is licensed under BSD-3-Clause license. Stay fair.
