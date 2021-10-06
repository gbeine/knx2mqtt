import yaml
import logging
import logging.config


class Config:
	"""Class for parsing knx2mqtt.yaml."""
	
	def __init__(self, file='logging.conf'):
		"""Initialize Config class."""
		logging.debug("Reading %s", file)
		try:
			with open(file, 'r') as f:
				D = yaml.load(f, Loader=yaml.SafeLoader)
				D.setdefault('version', 1)
				logging.config.dictConfig(D)
			self._mqtt = {}
			self._knx = {}
		except FileNotFoundError as ex:
			logging.error("Logging configuration file %s not found: %s", file, ex)
			exit(ex.errno)
	
	
	def read(self, file='knx2mqtt.yaml'):
		"""Read config."""
		logging.debug("Reading %s", file)
		try:
			with open(file, 'r') as filehandle:
				config = yaml.load(filehandle, Loader=yaml.SafeLoader)
				self._parse_mqtt(config)
				self._parse_knx(config)
		except FileNotFoundError as ex:
			logging.error("Configuration file %s not found: %s", file, ex)
			exit(ex.errno)


	def _parse_mqtt(self, config):
		"""Parse the mqtt section of knx2mqtt.yaml."""
		if "mqtt" in config:
			self._mqtt = config["mqtt"]

			if not "client_id" in self._mqtt:
				self._mqtt["port"] = "knx2mqtt"
			if not "host" in self._mqtt:
				raise ValueError("MQTT host not set")
			if not "port" in self._mqtt:
				self._mqtt["port"] = 1883
			if not "user" in self._mqtt:
				self._mqtt["user"] = ""
			if not "password" in self._mqtt:
				self._mqtt["port"] = ""
			if not "topic" in self._mqtt:
				raise ValueError("MQTT topic not set")
			if not "qos" in self._mqtt:
				self._mqtt["qos"] = 0
			if not "retain" in self._mqtt:
				self._mqtt["retain"] = False
			if not "keepalive" in self._mqtt:
				self._mqtt["keepalive"] = 60

		else:
			logging.error("MQTT configuration not found in configuration file.")
			exit(1)


	def _parse_knx(self, config):
		"""Parse the knx section of knx2mqtt.yaml."""
		if "knx" in config:
			self._knx = config["knx"]

			if "sensors" in self._knx:
				for item in self._knx["sensors"]:
					if not "address" in item:
						raise ValueError("Missing address for KNX sensor")
			else:
				self._knx["sensors"] = []

			if "switches" in self._knx:
				for item in self._knx["switches"]:
					if not "address" in item:
						raise ValueError("Missing address for KNX switch")
			else:
				self._knx["switches"] = []

		else:
			logging.error("KNX configuration not found in configuration file.")
			exit(1)


	def mqtt(self):
		return self._mqtt

	def knx(self):
		return self._knx
