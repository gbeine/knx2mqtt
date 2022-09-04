import yaml
import logging
import logging.config

from yaml.loader import SafeLoader


class Config:
	"""Class for parsing knx2mqtt.yaml."""
	
	def __init__(self):
		"""Initialize Config class."""
		with open('logging.conf') as f:
			D = yaml.safe_load(f)
			D.setdefault('version', 1)
			logging.config.dictConfig(D)
		self._mqtt = {}
		self._knx = {}
		self._items = []
	
	
	def read(self, file='knx2mqtt.yaml'):
		"""Read config."""
		logging.debug("Reading %s", file)
		try:
			with open(file, 'r') as filehandle:
				config = yaml.safe_load(filehandle)
				self._parse_mqtt_section(config)
				self._parse_knx_section(config)
				self._parse_items_section(config)
		except FileNotFoundError as ex:
			logging.error("Error while reading %s: %s", file, ex)


	def _parse_mqtt_section(self, config):
		"""Parse the mqtt section of knx2mqtt.yaml."""
		if 'mqtt' in config:
			self._mqtt = config['mqtt']
		if not 'host' in self._mqtt:
			raise ValueError('MQTT host not set')
		if not 'port' in self._mqtt:
			raise ValueError('MQTT port not set')
		if not 'user' in self._mqtt:
			raise ValueError('MQTT user not set')
		if not 'password' in self._mqtt:
			raise ValueError('MQTT password not set')
		if not 'topic' in self._mqtt:
			raise ValueError('MQTT topic not set')
		if not 'qos' in self._mqtt:
			self._mqtt['qos'] = 0
		if not 'retain' in self._mqtt:
			self._mqtt['retain'] = False
		if not 'json' in self._mqtt:
			self._mqtt['json'] = False


	def _parse_knx_section(self, config):
		"""Parse the knx section of knx2mqtt.yaml."""
		if 'knx' in config:
			self._knx = config['knx']
		if not 'individual_address' in self._knx:
			raise ValueError('KNX device address not set')
		if not 'tunneling' in self._knx:
			raise ValueError('Only tunneling is supported at the moment')
		if not 'local_ip' in self._knx['tunneling']:
			raise ValueError('KNX tunneling requires local IP address')
		if not 'host' in self._knx['tunneling']:
			raise ValueError('KNX tunneling requires gateway IP address')
		if not 'port' in self._knx['tunneling']:
			self._knx['tunneling']['port'] = 3671


	def _parse_items_section(self, config):
		"""Parse the items section of knx2mqtt.yaml."""
		if 'items' in config:
			for item in config['items']:
				try:
					i = Item(item)
					self._items.append(i)
				except ValueError as ex:
					logging.error("Error while parsing item: %s", ex)


	def mqtt(self):
		return self._mqtt


	def knx(self):
		return self._knx


	def items(self):
		return self._items


class Item:
	"""Class for a single item in the knx2mqtt.yaml"""

	def __init__(self, item):
		self._address        = item['address']        if 'address' in item else None
		self._type           = item['type']           if 'type' in item else None
		self._mqtt_subscribe = item['mqtt_subscribe'] if 'mqtt_subscribe' in item else False
		self._mqtt_publish   = item['mqtt_publish']   if 'mqtt_publish' in item else True
		self._knx_subscribe  = item['knx_subscribe']  if 'knx_subscribe' in item else True
		self._knx_publish    = item['knx_publish']    if 'knx_publish' in item else False
		self._mqtt_topics    = item['mqtt_topics']    if 'mqtt_topics' in item else []
		self._knx_addresses  = item['knx_addresses']  if 'knx_addresses' in item else []
		if self._address is None:
			raise ValueError("No address defined for item: %s", item)
		if self._type is None:
			raise ValueError("No type defined for item: %s", item)

	def address(self):
		return self._address

	def type(self):
		return self._type

	def mqtt_subscribe(self):
		return self._mqtt_subscribe

	def mqtt_publish(self):
		return self._mqtt_publish

	def knx_subscribe(self):
		return self._knx_subscribe

	def knx_publish(self):
		return self._knx_publish

	def mqtt_topics(self):
		return self._mqtt_topics

	def knx_addresses(self):
		return self._knx_addresses
