import unittest

from unittest.mock import MagicMock

from paho.mqtt.client import MQTTMessage

from knx2mqtt.mqtt import MQTT
from knx2mqtt.knx import KNX
from knx2mqtt.mqtt2knx import mqtt2knx

class TestMqtt2Knx(unittest.TestCase):
    def test_on_message(self):

        mqtt_mock = MQTT(None)
        mqtt_mock.get_plain_topic = MagicMock(return_value='4/2/3')
        mqtt_mock.set_message_cb = MagicMock() # required in initialization
        mqtt_mock.set_connect_cb = MagicMock() # required in initialization

        knx_mock = KNX([])
        knx_mock.publish = MagicMock()

        m2k = mqtt2knx(knx_mock, mqtt_mock)

        # topic consist of base topic and group address
        message = MQTTMessage(topic=b'home/bus/knx/4/2/3')
        # payload must be bytes, containing e.g. a target temperature as string
        message.payload = b'23.5'

        m2k.on_message(None, None, message)

        # assert expected calls on MQTT and KNX
        mqtt_mock.get_plain_topic.assert_called_with('home/bus/knx/4/2/3')
        knx_mock.publish.assert_called_with('4/2/3', '23.5')


if __name__ == '__main__':
    unittest.main()
