import logging
import asyncio

from xknx import XKNX
from xknx.knx import AddressFilter, GroupAddress, Telegram, TelegramType, TelegramDirection

class Knx:

	def __init__(self, config):
		self._config = config
		self._address_filters = list()
		self._subscription_filters = list()
		for sensor in self._config['sensors']:
			if not ('expose' in sensor and sensor['expose']):
				self._address_filters.append(AddressFilter(sensor['address']))
			if ('expose' in sensor and sensor['expose']) or ('subscribe' in sensor and sensor['subscribe']):
				self._subscription_filters.append(sensor['address'])
		for switch in self._config['switches']:
			if not ('expose' in switch and switch['expose']):
				self._address_filters.append(AddressFilter(switch['address']))
			if ('expose' in switch and switch['expose']) or ('subscribe' in switch and switch['subscribe']):
				self._subscription_filters.append(switch['address'])


	def connect(self):
		self._xknx = XKNX()


	def set_telegram_cb(self, cb):
		self._xknx.telegram_queue.register_telegram_received_cb(cb, self._address_filters)


	def get_subscriptions(self):
		return self._subscription_filters


	def get_dpttype(self, group_address):
		logging.debug("Try to get type for group address {0}".format(group_address))
		dpttype = next((sensor['type'] for sensor in self._config['sensors'] if sensor['address'] == group_address), None)
		if not dpttype:
			dpttype = next((switch['type'] for switch in self._config['switches'] if switch['address'] == group_address), None)
		return dpttype


	def publish(self, group_address, payload):
		logging.debug("Try to publish payload {0} for group address {1}".format(payload, group_address))
		telegram = Telegram(direction=TelegramDirection.OUTGOING)
		telegram.group_address = group_address
		telegram.telegramtype = TelegramType.GROUP_WRITE
		telegram.payload = payload

		logging.debug(telegram)

		if self._xknx.started:
#			loop = asyncio.new_event_loop()
#			asyncio.set_event_loop(loop)
#			loop.run_until_complete(self._xknx.telegrams.put(telegram))
			asyncio.run(self._xknx.telegrams.put(telegram))
#			loop.run_until_complete(self._xknx.telegram_queue.process_telegram_outgoing(telegram))
#			asyncio.run(self._xknx.telegram_queue.process_telegram_outgoing(telegram))
			logging.info("Sent")
		else:
			logging.info("XKNX not started")


	async def run(self):
		await self._xknx.start(daemon_mode=True)
		await self._xknx.stop()
