import traceback
import logging
import importlib

from xknx import telegram


class knx2mqtt:

	def __init__(self, knx, mqtt):
		self._knx = knx
		self._mqtt = mqtt
		self._knx.set_telegram_cb(self.on_telegram_received)


	async def on_telegram_received(self, telegram):
		try:
			logging.info("KNX2MQTT {}".format(telegram))
			if telegram.direction != TelegramDirection.INCOMING:
				return

			group_address = str(telegram.destination_address)
			payload = telegram.payload


			return True

		except Exception as e:
			logging.error(traceback.format_exc())
