import yaml
import logging
import logging.config


class Config:
	"""Class for parsing knx2mqtt.yaml."""
	
	def __init__(self):
		"""Initialize Config class."""
#		logging.config.dictConfig(yaml.load('logging.conf', Loader=yaml.SafeLoader))
		with open('logging.conf') as f:
			D = yaml.load(f, Loader=yaml.SafeLoader)
			D.setdefault('version', 1)
			logging.config.dictConfig(D)
		self._mqtt = {}
		self._knx = {}
	
	
	def read(self, file='knx2mqtt.yaml'):
		"""Read config."""
		logging.debug("Reading %s", file)
		try:
			with open(file, 'r') as filehandle:
				config = yaml.load(filehandle, Loader=yaml.SafeLoader)
				self._parse_mqtt(config)
				self._parse_knx(config)
		except FileNotFoundError as ex:
			logging.error("Error while reading %s: %s", file, ex)


	def _parse_mqtt(self, config):
		"""Parse the mqtt section of knx2mqtt.yaml."""
		if "mqtt" in config:
			self._mqtt = config["mqtt"]
		if not "host" in self._mqtt:
			raise ValueError("MQTT host not set")
		if not "port" in self._mqtt:
			raise ValueError("MQTT port not set")
		if not "user" in self._mqtt:
			raise ValueError("MQTT user not set")
		if not "password" in self._mqtt:
			raise ValueError("MQTT password not set")
		if not "topic" in self._mqtt:
			raise ValueError("MQTT topic not set")
		if not "qos" in self._mqtt:
			self._mqtt["qos"] = 0
		if not "retain" in self._mqtt:
			self._mqtt["retain"] = False


	def _parse_knx(self, config):
		"""Parse the knx section of knx2mqtt.yaml."""
		if "knx" in config:
			self._knx = config["knx"]
		for item in self._knx["sensors"]:
			if not "address" in item:
				raise ValueError("Missing address for KNX sensor")
		for item in self._knx["switches"]:
			if not "address" in item:
				raise ValueError("Missing address for KNX switch")


	def mqtt(self):
		return self._mqtt

	def knx(self):
		return self._knx
