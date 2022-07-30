import asyncio
import time

from knx2mqtt import mqtt
from knx2mqtt import mqtt2knx
from knx2mqtt.knx import KNX
from knx2mqtt.knx2mqtt import knx2mqtt

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
		self._mqtt = mqtt.Mqtt(self._config.mqtt())
		self._mqtt.connect()

	def _init_knx(self):
		self._knx = KNX(self._config.knx())
		self._knx.connect()

	def _init_callbacks(self):
		mqtt2knx.mqtt2knx(self._knx, self._mqtt, s)
		knx2mqtt(self._knx, self._mqtt)
