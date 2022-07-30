import asyncio
import time

from knx2mqtt.mqtt import MQTT
from knx2mqtt.knx import KNX
from knx2mqtt.knx2mqtt import knx2mqtt
from knx2mqtt.mqtt2knx import mqtt2knx

class Daemon:

	def __init__(self, config):
		self._config = config
		self._init_mqtt()
		self._init_knx()
		self._init_callbacks()

	def run(self):
		self._mqtt.run()
		loop = asyncio.get_event_loop()
		loop.run_until_complete(self._knx.run())
		loop.close()

	def _init_mqtt(self):
		self._mqtt = MQTT(self._config.mqtt(), self._config.items())
		self._mqtt.connect()

	def _init_knx(self):
		self._knx = KNX(self._config.items())
		self._knx.connect()

	def _init_callbacks(self):
		knx2mqtt(self._knx, self._mqtt)
		mqtt2knx(self._knx, self._mqtt)
