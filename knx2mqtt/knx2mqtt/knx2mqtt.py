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
			group_address = str(telegram.group_address)
			payload = telegram.payload

			dpttype = self._knx.get_dpttype(group_address)

			if dpttype is None:
				logging.info("No DPTType found for address {0}".format(group_address))
				return True
			elif dpttype == "DPTBinary":
				logging.debug("{0} {1}".format(group_address, dpttype))
				value = payload.value
			else:
				logging.debug("{0} {1}".format(group_address, dpttype))
				dptcls = getattr(importlib.import_module(XKNX_DPT_MODULE_STR), dpttype)
				value = dptcls.from_knx(payload.value)

			logging.debug("{0} {1}".format(payload, value))

			if not self._states.is_state(group_address, value):
				self._states.set_state(group_address, value)
				self._mqtt.publish(group_address, value)

			# HACK!
			self._knx._xknx.started = True

			return True

		except Exception as e:
			logging.error(traceback.format_exc())
