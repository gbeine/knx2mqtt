import traceback
import logging
import importlib

from xknx.dpt import DPTArray, DPTBinary
from xknx.telegram import GroupAddress
XKNX_DPT_MODULE_STR = "xknx.dpt"


class mqtt2knx:

	def __init__(self, knx, mqtt, states):
		self._knx = knx
		self._mqtt = mqtt
		self._states = states
		self._subscriptions = self._knx.get_subscriptions()
		self._mqtt.set_message_cb(self.on_message)
		self._mqtt.set_connect_cb(self.on_connect)


	def on_message(self, client, userdata, message):
		try:
			logging.info("MQTT connection callback")
			topic = message.topic
			payload = str(message.payload.decode())

			logging.debug("Message {0} for topic {1}".format(payload, topic))

			address = self._mqtt.get_plain_topic(topic)

			logging.debug("Group address for {0} is {1}".format(topic, address))

			if not self._states.is_state(address, payload):

				self._states.set_state(address, payload)

				dpttype = self._knx.get_dpttype(address)

				if dpttype is None:
					logging.info("No DPTType found for address {0}".format(address))
					return True
				elif dpttype == "DPTBinary":
					value = DPTBinary(int(payload))
				else:
					dptcls = getattr(importlib.import_module(XKNX_DPT_MODULE_STR), dpttype)
					value = DPTArray(dptcls.to_knx(payload))

				group_address = GroupAddress(address)

				logging.info("New value for KNX {0} is {1}".format(group_address, value))

				self._knx.publish(group_address, value)

			return True

		except Exception as e:
			logging.error(traceback.format_exc())


	def on_connect(self, client, userdata, flags, rc):
		try:
			logging.info("MQTT connection callback")

			for topic in self._subscriptions:
				self._mqtt.subscribe(topic)

			return True

		except Exception as e:
			logging.error(traceback.format_exc())
