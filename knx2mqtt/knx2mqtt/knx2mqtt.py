import traceback
import logging
import importlib
XKNX_DPT_MODULE_STR = "xknx.dpt"


class knx2mqtt:

	def __init__(self, knx, mqtt, states):
		self._knx = knx
		self._mqtt = mqtt
		self._states = states
		self._knx.set_telegram_cb(self.callback)


	async def callback(self, telegram):
		try:
			logging.info("KNX2MQTT {}".format(telegram))
			group_address = str(telegram.destination_address)
			payload = telegram.payload.value

			dpttype = self._knx.get_dpttype(group_address)
			dpttype_auto = payload.__class__.__name__

			if dpttype is None:
				logging.info("No DPTType found for address {0}".format(group_address))
				return True
			elif dpttype == "DPTBinary":
				logging.debug("group address: {0}; dpttype by user: {1}; dpttype detected: {2};".format(group_address, dpttype, dpttype_auto))
				value = payload.value
			else:
				logging.debug("group address: {0}; dpttype by user: {1}; dpttype detected: {2};".format(group_address, dpttype, dpttype_auto))
				dptcls = getattr(importlib.import_module(XKNX_DPT_MODULE_STR), dpttype)
				value = dptcls.from_knx(payload.value)

			logging.debug("payload: {0}; value: {1};".format(payload, value))

			if not self._states.is_state(group_address, value):
				self._states.set_state(group_address, value)
				self._mqtt.publish(group_address, value)

			# HACK!
			self._knx._xknx.started = True

			return True

		except Exception as e:
			logging.error(traceback.format_exc())
