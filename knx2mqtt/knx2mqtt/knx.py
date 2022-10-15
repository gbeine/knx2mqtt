import asyncio
import logging
import importlib
import socket

from xknx import XKNX
from xknx.dpt.dpt import DPTArray, DPTBinary
from xknx.io.knxip_interface import ConnectionType, ConnectionConfig
from xknx.telegram.address import GroupAddress, IndividualAddress
from xknx.telegram.apci import GroupValueWrite
from xknx.telegram.telegram import Telegram, TelegramDirection

XKNX_DPT_MODULE_STR = "xknx.dpt"

class KNX:

	def __init__(self, config, items):
		self._config = config
		self._subscription_addresses = [] # this list contains all the addresses to subscribe
		self._publishing_addresses = [] # this list contains all the addresses to publish
		self._published_values = {} # this dict contains the last value published to a certain address
		self._configured_items = {}
		for item in items:
			if item.knx_publish():
				self._add_item_to_publish(item)
			if item.knx_subscribe():
				self._add_item_to_subscribe(item)


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
			if dpt_type == 'DPTBinary':
				value = bool(payload.value.value)
			else:
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
			if dpt_type == 'DPTBinary' and type(value) == str:
				payload = DPTBinary(int(value.lower() == 'true'))
			elif dpt_type == 'DPTBinary' and type(value) == bool:
				payload = DPTBinary(int(value == True))
			else:
				dpt_class = getattr(importlib.import_module(XKNX_DPT_MODULE_STR), dpt_type)
				payload = DPTArray(dpt_class.to_knx(value))
			return payload
		except Exception as e:
			logging.error("DPT type not found for address {0}".format(group_address))
			logging.error(traceback.format_exc())
			return None


	def publish(self, item_address, value):
		logging.debug("Try to publish value {0} for group address {1}".format(value, item_address))

		if item_address not in self._publishing_addresses:
			logging.info("Publish to address {0} is not allowed".format(item_address))
			return False

		if item_address in self._published_values and self._published_values[item_address] == value:
			logging.debug("Current value for address {0} did not change, will not publish".format(item_address))
			# maybe allowing to force publishing should be an option?
			return False

		addresses = [ self._configured_items[item_address].address() ]
		addresses.extend(self._configured_items[item_address].knx_addresses())
		logging.debug("Publishing to address {0} will done for {1} addresses".format(item_address, len(addresses)))

		payload = self.get_payload_to_knx(item_address, value)

		if payload is None:
			return False

		for address in addresses:
			self._publish_value(address, payload)
			self._published_values[address] = payload

		return True


	def connect(self):
		self._xknx = XKNX(
			daemon_mode=True,
			own_address=self._get_individual_address(),
			connection_config=self._get_connection_config()
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

		group_value = GroupValueWrite(value)

		telegram = Telegram(
			destination_address=group_address,
			direction=TelegramDirection.OUTGOING,
			payload=group_value,
			source_address=self._get_individual_address()
		)

		logging.debug("KNX2MQTT Telegram {0}".format(telegram))

		if self._xknx.started and self._xknx.connected:
			if 'no_queue' in self._config and self._config['no_queue']:
				asyncio.run(self._xknx.telegram_queue.process_telegram_outgoing(telegram))
			else:
				asyncio.run(self._xknx.telegrams.put(telegram))
			# self._xknx.telegrams.put_nowait(telegram)
			# self._xknx.telegrams.put(telegram)
			logging.debug("KNX2MQTT Telegram sent")
		else:
			logging.error("XKNX not started")


	def _get_connection_config(self):
		# TODO: currently only tunneling is supported, add more! ;-)
		return ConnectionConfig(
			connection_type=ConnectionType.TUNNELING,
			local_ip=self._config['tunneling']['local_ip'],
			gateway_ip=socket.gethostbyname(self._config['tunneling']['host']),
			gateway_port=self._config['tunneling']['port']
		)


	def _get_individual_address(self):
		return IndividualAddress(self._config['individual_address'])


	def _add_item_to_publish(self, item):
		address = item.address()
		self._publishing_addresses.append(address)
		self._published_values[address] = None
		self._configured_items[address] = item
		for address in item.knx_addresses():
			self._publishing_addresses.append(address)
			self._published_values[address] = None


	def _add_item_to_subscribe(self, item):
		address = item.address()
		self._subscription_addresses.append(GroupAddress(address))
		self._configured_items[address] = item
		for address in item.knx_addresses():
			self._subscription_addresses.append(GroupAddress(address))
