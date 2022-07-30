import asyncio
import logging
import importlib

from xknx import XKNX
from xknx.dpt.dpt import DPTArray, DPTBinary
from xknx.telegram import AddressFilter, GroupAddress, Telegram, TelegramDirection

class KNX:

	def __init__(self, config):
		self._config = config
		self._subscription_addresses = list() # this list contains all the addresses to subscribe
		self._publishing_addresses = {} # this dict contains the item configuration for all addresses to publish
		self._published_values = {} # this dict contains the last value published to a certain address
		for item in self._config:
			if item.knx_publish():
				self._publishing_addresses[item.address()] = item
				self._published_values[item.address()] = None
				for address in item.knx_addresses():
					self._publishing_addresses[address] = item
					self._published_values[address] = None
			if item.knx_subscribe():
				self._subscription_addresses.append(item.address())
				for address in item.knx_addresses():
					self._subscription_addresses.append(address)

	def connect(self):
		self._xknx = XKNX(
			config='xknx.yaml', daemon_mode=True
		)


	def set_telegram_cb(self, telegram_received_cb):
		self._xknx.telegram_queue.register_telegram_received_cb(
			telegram_received_cb, self._subscription_addresses
		)


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
		await self._xknx.start()
		await self._xknx.stop()

