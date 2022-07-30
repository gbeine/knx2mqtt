import asyncio
import logging
import importlib

from xknx import XKNX
from xknx.dpt.dpt import DPTArray, DPTBinary
from xknx.telegram import GroupAddress, Telegram, TelegramDirection

class KNX:

	def __init__(self, config):
		self._config = config
		self._subscription_addresses = list() # this list contains all the addresses to subscribe
		self._publishing_addresses = [] # this dict contains the item configuration for all addresses to publish
		self._published_values = {} # this dict contains the last value published to a certain address
		self._configured_items = {}
		for item in self._config:
			item_added = False
			if item.knx_publish():
				self._add_item_to_publish(item)
				item_added = True
			if item.knx_subscribe():
				self._add_item_to_subscribe(item)
				item_added = True
			if item_added:
				self._configured_items[item.address()] = item


	def set_telegram_cb(self, telegram_received_cb):
		self._xknx.telegram_queue.register_telegram_received_cb(
			telegram_received_cb=telegram_received_cb, group_addresses=self._subscription_addresses
		)


	def get_payload_from_knx(self, group_address, payload):
		logging.debug("Try to get payload value for address {0}".format(group_address))
		dpt_type = self._get_dpt_type(group_address)

		if dpt_type is None:
			logging.info("No DPT type found for address {0}".format(group_address))
			return None

		logging.debug("Address {0} has DPT type {1}".format(group_address, dpt_type))

		try:
			dpt_class = getattr(importlib.import_module("xknx.dpt"), dpt_type)
			value = dpt_class.from_knx(payload.value.value)
			return value
		except Exception as e:
			logging.error("DPT type not found for address {0}".format(group_address))
			logging.error(traceback.format_exc())
			return None


	def get_payload_to_knx(self, group_address, value):
		dpt_type = self._get_dpt_type(group_address)
		if dpt_type is None:
			logging.info("No DPT type found for address {0}".format(group_address))
			return None

		logging.debug("DPT type for address {0} is {1}".format(group_address, dpt_type))

		try:
			dpt_class = getattr(importlib.import_module('xknx.dpt'), dpt_type)
			payload = DPTArray(dpt_class.to_knx(value))  # TODO: use binary as option
			return payload
		except Exception as e:
			logging.error("DPT type not found for address {0}".format(group_address))
			logging.error(traceback.format_exc())
			return None


	def publish(self, group_address, value):
		logging.debug("Try to publish value {0} for group address {1}".format(value, group_address))

		if group_address not in self._publishing_addresses:
			logging.debug("Publish to address {0} is not allowed".format(group_address))
			return False

		if group_address in self._published_values and self._published_values[group_address] == value:
			logging.debug("Current value for address {0} did not change, will not publish".format(group_address))
			# maybe allowing to force publishing should be an option?
			return False

		addresses = [ self._configured_items[group_address].address() ]
		addresses.extend(self._configured_items[group_address].knx_addresses())
		logging.debug("Publishing to address {0} will done for {1} addresses".format(group_address, len(addresses)))

		payload = get_payload_to_knx(group_address, value)

		if payload is None:
			return False

		for address in addresses:
			self._publish_value(address, payload)
			self._published_values[address] = payload

		return True


	def connect(self):
		self._xknx = XKNX(
			config='xknx.yaml', daemon_mode=True
		)


	async def run(self):
		await self._xknx.start()
		await self._xknx.stop()


	def _get_dpt_type(self, group_address):
		logging.debug("Try to get type for group address {0}".format(group_address))
		dpt_type = self._configured_items[group_address].type() if group_address in self._configured_items else None

		return dpt_type


	def _publish_value(self, address, value):
		logging.debug("Publish value {0} for group address {1}".format(value, address))

		group_address = GroupAddress(address)

		telegram = Telegram(
			destination_address=group_address, payload=value
		)
		telegram.destination_address = group_address
		telegram.payload = value

		logging.debug(telegram)

		self._xknx.telegrams.put(telegram)


	def _add_item_to_publish(self, item):
		self._publishing_addresses.append(item.address())
		self._published_values[item.address()] = None
		for address in item.knx_addresses():
			self._publishing_addresses.append(address)
			self._published_values[address] = None


	def _add_item_to_subscribe(self, item):
		self._subscription_addresses.append(GroupAddress(item.address()))
		for address in item.knx_addresses():
			self._subscription_addresses.append(GroupAddress(address))
