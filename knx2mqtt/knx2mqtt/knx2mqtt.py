import traceback
import logging
import importlib

from xknx.telegram import TelegramDirection


class knx2mqtt:

	def __init__(self, knx, mqtt):
		logging.info("KNX2MQTT - initialise knx2mqtt routing")
		self._knx = knx
		self._mqtt = mqtt
		self._knx.set_telegram_cb(self.on_telegram_received)


	async def on_telegram_received(self, telegram):
		try:
			logging.debug("KNX2MQTT: Telegram {}".format(telegram))
			if telegram.direction != TelegramDirection.INCOMING:
				return

			group_address = str(telegram.destination_address)
			payload = self._knx.get_payload_from_knx(group_address, telegram.payload)

			if payload is None:
				return

			logging.info("KNX2MQTT: Telegram for address {0} with payload {1}".format(group_address, payload))

			self._mqtt.publish(group_address, payload)

			return

		except Exception as e:
			logging.error(traceback.format_exc())
