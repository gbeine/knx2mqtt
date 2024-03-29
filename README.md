# knx2mqtt - A KNX2MQTT Bridge allowing bidirectional telegram transfer

I've created this project as a replacement for the KNX integration of [HomeAssistant](https://home-assistant.io/) that worked not stable in my environment.

It is quite simple and does what it's name says: It works as a bridge between KNX and MQTT tranlating messages between these in both directions.

## Installation

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

- copy ```knx2mqtt.conf.example```
- configure as you like

| option                 | default              | arguments                | comment                                                            |
|------------------------|----------------------|--------------------------|--------------------------------------------------------------------|
| mqtt_host              | 'localhost'          | -m, --mqtt_host          | The hostname of the MQTT server.                                   |
| mqtt_port              | 1883                 | --mqtt_port              | The port of the MQTT server.                                       |
| mqtt_keepalive         | 30                   | --mqtt_keepalive         | The keep alive interval for the MQTT server connection in seconds. |
| mqtt_clientid          | 'fronius2mqtt'       | --mqtt_clientid          | The clientid to send to the MQTT server.                           |
| mqtt_user              | -                    | -u, --mqtt_user          | The username for the MQTT server connection.                       |
| mqtt_password          | -                    | -p, --mqtt_password      | The password for the MQTT server connection.                       |
| mqtt_topic             | 'fronius'            | -t, --mqtt_topic         | The topic to publish MQTT message.                                 |
| knx_host               | 'localhost'          | --knx_host               | The address of the KNX tunnel device.                              |
| knx_port               | 3671                 | --knx_port               | The port of the KNX tunnel device.                                 |
| knx_local_ip           | -                    | --knx_local_ip           | The ip address of the system that connects to KNX.                 |
| knx_individual_address | -                    | --knx_individual_address | The group address of the system that send telegrams to KNX.        |
| knx_no_queue           | -                    | --knx_no_queue           | Workaround for scheduling problems of XKNX telegram queue.         |
| verbose                | -                    | -v, --verbose            | Be verbose while running.                                          |
| -                      | '/etc/knx2mqtt.conf' | -c, --config             | The path to the config file.                                       |
| items                  | see below            | -                        | The configuration for the items on the KNX bus.                    |

### KNX

Currently, only KNX tunneling mode is supported.
It may become more in the future, if I found testing environments with according setups.
Feel free to add routing or other options and open a pull request for this.

### Items

Then you can configure your bus topology as items.

```
    ...
    "items": [
        {
            "address": "5/0/10",
            "type": "DPTTemperature"
        },
        {
            "address": "5/0/20",
            "type": "DPTHumidity"
        },
        ...
    ]
    ...
```

Each item need an `address` (the group address) and a `type`.
Unfortunately, the list of types is not part of the xknx documentation.
But the examples in the file I provide with the project may fit for the most purposes.
All supported types can be found in the [xknx sources](https://github.com/XKNX/xknx/blob/main/xknx/dpt/__init__.py).

The default operating mode for an object is to listen on the KNX and publish the telegram values to MQTT.

That may be changed using the following settings:

* `mqtt_subscribe` (default: false): if set to `true`, changes on any related MQTT topic will be processed

### Publishing

All values are published using the group address and the MQTT topic.

So, the Date exposing sensor in the example is listening for `home/bus/knx/0/0/1` and the switch is listening on and publishing to `home/bus/knx/0/1/1`.

## Running knx2mqtt

I use [systemd](https://systemd.io/) to manage my local services.

## Support

I have not the time (yet) to provide professional support for this project.
But feel free to submit issues and PRs, I'll check for it and honor your contributions.

## License

The whole project is licensed under MIT license. Stay fair.
