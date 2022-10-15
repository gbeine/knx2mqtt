import traceback
import logging
import importlib

from xknx.telegram import GroupAddress
from xknx.dpt import DPTBinary, DPTArray

class mqtt2knx:

	def __init__(self, knx, mqtt):
		logging.info("KNX2MQTT - initialise mqtt2knx routing")
		self._knx = knx
		self._mqtt = mqtt
		self._mqtt.set_message_cb(self.on_message)


	def on_message(self, address, payload):
		try:
			logging.info("MQTT: Publish value {0} for address {1}".format(payload, address))
			self._knx.publish(address, payload)
		except Exception as e:
			logging.error(traceback.format_exc())

		return True
