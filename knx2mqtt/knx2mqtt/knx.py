import logging
import asyncio
import socket

from xknx import XKNX
from xknx.io import ConnectionConfig, ConnectionType
from xknx.telegram import AddressFilter, GroupAddress, GroupAddressType, Telegram, TelegramDirection
from xknx.telegram.apci import GroupValueWrite

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
		# General configuration for xknx
		gen_params = {}
		if 'general' in self._config:
			gen_params = self._config['general']
			if 'address_format' in gen_params:
				addr_format_str = str(gen_params['address_format']).upper()
				gen_params['address_format'] = GroupAddressType[addr_format_str]
				logging.debug("KNX address format is {0}".format(gen_params['address_format']))			

		# Connection configuation
		conn_type = ConnectionType.AUTOMATIC
		conn_params = {}
		if 'connection' in self._config:
			if 'routing' in self._config['connection']:
				conn_type = ConnectionType.ROUTING
				conn_params = self._config['connection']['routing']
			elif 'tunneling' in self._config['connection']:
				conn_type = ConnectionType.TUNNELING
				conn_params = self._config['connection']['tunneling']

				# Resolve gateway ip, if needed
				conn_params['gateway_ip'] = socket.gethostbyname(conn_params['gateway_ip'])
				
		conn_config = ConnectionConfig(**conn_params, connection_type=conn_type)
		logging.debug("KNX connection type is {0}".format(conn_type))

		# Setup XKNX
		self._xknx = XKNX(**gen_params, daemon_mode=True, connection_config=conn_config)
		logging.info("XKNX instance (version %s) for connection to KNX gateway %s created." % (self._xknx.version, conn_config.gateway_ip))


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

		telegram = Telegram(
			direction = TelegramDirection.OUTGOING,
            destination_address = group_address,
            payload = GroupValueWrite(payload),
        )

		logging.debug("Publishing telegram: {0}".format(telegram))

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
