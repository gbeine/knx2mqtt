# knx2mqtt - A KNX2MQTT Bridge allowing bidirectional telegram transfer

I've created this project as a replacement for the KNX integration of [HomeAssistant](https://home-assistant.io/) that worked not stable in my environment.

It is quite simple and does what it's name says: It works as a bridge between KNX and MQTT tranlating messages between these in both directions.

## Installation

The installation required Python 3.7 (it should work with Python 3.5 and 3.6 as well) and `git`.

I usually install my own services under `/opt/services`.
So, it works out of the box, if you just do:

```
mkdir -p /opt/services
cd /opt/services
git clone https://github.com/gbeine/knx2mqtt.git
cd knx2mqtt
./install
```

The `install` script creates a virtual python environment using the `venv` module.
All required libraries are installed automatically.

## Configuration

There are two configuration files: `xnkx.yaml` and `knx2mqtt.yaml`.

The first one is for the [xknx](https://xknx.io/) library.
An example is included, more details you will find in the [xknx documentation](https://xknx.io/configuration).

The `knx2mqtt.yaml` is where the magic happens.

### MQTT

First, you need to configure your MQTT server.

```
mqtt:
    host: your.mqtt-server.name
    port: 1883
    user: knx2mqtt
    password: topsecret
    topic: "home/bus/knx"
    qos: 0
    retain: true
```

Usually, you only need to change the `host`, `user` and `password`.
Maybe, you want to use another `topic`.
Leave `qos` and `retain` unless you know what these parameters do.

### KNX

Then you can configure your KNX bus topology.
At the moment the bridge supports sensors and switches.

```
knx:
    sensors:
    ...
    switches:
    ...
```

Each item (sensors and switches) need an `address` (the group address) and a `type`.
Unfortunately, the list of types is not part of the xknx documentation.
But the examples in the file I provide with the project may fit for the most purposes.

The default operating mode for an object is to listen on the KNX and publish the telegram values to MQTT.

That may be changed by setting `expose` or `subscribe` to `true`.

If `expose` is `true`, values published on MQTT will be sent as telegram to KNX. Values from KNX are never published to MQTT.

```
knx:
    sensors:
        - address: 0/0/1
          type: DPTDate
          expose: true
```

If `subscribe` is `true`, the bridge works in bidirectional mode. Values from KNX are published to MQTT and vice versa.

```
knx:
    switches:
        - address: 0/1/1
          type: DPTBinary
          subscribe: true
```

### Publishing

All values are published using the group address and the MQTT topic.

So, the Date exposing sensor in the example is listening for `home/bus/knx/0/0/1` and the switch is listening on and publishing to `home/bus/knx/0/1/1`.

## Running knx2mqtt

I use [Supervisor](http://supervisord.org/) to manage my local services.

For this, a configuration file and an executable are part of the project.

The configuration file is located under `supervisor`, just copy or link it to `/etc/supervisor/conf.d`.

The `run` script expects an environment variable named `LOGDIR` where the logfile should be written. This is set by the supervisor configuration, so change it there.

## Support

I have not the time (yet) to provide professional support for this project.
But feel free to submit issues and PRs, I'll check for it and honor your contributions.

## License

The whole project is licensed under MIT license. Stay fair.