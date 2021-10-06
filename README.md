# knx2mqtt - A KNX2MQTT Bridge allowing bidirectional telegram transfer

I've created this project as a replacement for the KNX integration of [HomeAssistant](https://home-assistant.io/) that worked not stable in my environment.

It is quite simple and does what it's name says: It works as a bridge between KNX and MQTT translating messages between these in both directions.
It can also perfectly be used to route KNX messages between several KNX installations, e.g., if you have an indoor and an outdoor setup.

## Installation

### Native environment
The installation requires minimum Python 3.8 and `git`.

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

### Docker environment
To run the app in a container, you need to have a running Docker installation.
You can either build the container manually or use the provided `docker-compose` file.  

Using plain docker:
```
(...)
cd knx2mqtt
docker build -t knx2mqtt .
```

Using docker-compose, the image build process is covered automatically. 
If you want to trigger the build manually, run:
```
(...)
cd knx2mqtt
docker-compose build
```

## Configuration

There is one configuration file: `knx2mqtt.yaml`.
It is where the magic happens. It contains the configuration for KNX and MQTT.

### MQTT

First, you need to configure your MQTT server.

```
mqtt:
  client_id: knx2mqtt
  host: your.mqtt-server.name
  port: 1883
  user: knx2mqtt
  password: topsecret
  topic: "home/bus/knx"
  qos: 0
  retain: true
  keepalive: 60
```

Usually, you only need to change the `host`, `user` and `password`.
Maybe, you want to use another `topic`.
Leave `qos` and `retain` unless you know what these parameters do.

### KNX

Then you can configure your KNX bus topology.  

First, you need to configure your KNX gateway.
```
knx:
  general:
    own_address: '15.15.249'
    #address_format: long
    #rate_limit: 200
    #multicast_group: '224.0.23.12'
    #multicast_port: 3671
  connection:
    #routing:
      #local_ip: 192.168.0.12
    tunneling:
      gateway_ip: '192.168.0.11'
      gateway_port: 3671
      local_ip: '192.168.0.12'
      #local_port: 12399
      #route_back: false
```
If you are going to use knx2mqtt in a container, check the related section for configuration details.

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

#### KNX configuration for container
When running the app in a container, you need to configure the KNX library accordingly.
Set ‘route_back’ to True or use host network mode.
```
knx:
  connection:
    tunneling:
      gateway_ip: '192.168.0.11'
      #gateway_port: 3671
      local_port: 12399
      route_back: True
```
The port `12399/udp` is exposed by the container.  
  
You can also use the following environment variables:  
`LOGDIR` path to log files.  
`LOGCONFIG_FILE` path to configuration file for logging options (use `/config/logging.production.conf` for producation and `/config/logging.conf` for debugging).  
`CONFIG_FILE` path to main knx2mqqt configuration file.  
`KNX_LOCAL_PORT` default local UDP port used by knx2mqtt for KNX gateway communication.  
  
The default values are defined in the file `Dockerfile`.


### Publishing

All values are published using the group address and the MQTT topic.

So, the Date exposing sensor in the example is listening for `home/bus/knx/0/0/1` and the switch is listening on and publishing to `home/bus/knx/0/1/1`.


## Running knx2mqtt

### Run as native app

I use [Supervisor](http://supervisord.org/) to manage my local services.

For this, a configuration file and an executable are part of the project.

The configuration file is located under `supervisor`, just copy or link it to `/etc/supervisor/conf.d`.

The `run` script expects an environment variable named `LOGDIR` where the logfile should be written. This is set by the supervisor configuration, so change it there.

### Run as container

You can either run the container manually or use the provided `docker-compose` file.  

The configuration file `knx2mqtt.yaml` must be mounted into the container at `/config/knx2mqtt.yaml`, otherwise the container won't start.

Using plain docker:
```
docker run --rm --name knx2mqtt -v $PWD/knx2mqtt.yaml:/app/knx2mqtt.yaml knx2mqtt
```

Using docker-compose adjust your settings in `docker-compose.yaml` first. Then run:
```
cd knx2mqtt
docker-compose up -d
```

## Support

I have not the time (yet) to provide professional support for this project.
But feel free to submit issues and PRs, I'll check for it and honor your contributions.

## License

The whole project is licensed under MIT license. Stay fair.