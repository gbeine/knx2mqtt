import traceback
import logging
import paho.mqtt.client as mqtt

class Mqtt:

	def __init__(self, config):
		self._config = config


	def connect(self):
		self._client = mqtt.Client()
		self._client.username_pw_set(self._config['user'], self._config['password'])


	def disconnect(self):
		self.client.disconnect()


	def set_message_cb(self, cb):
		self._client.on_message = cb


	def set_connect_cb(self, cb):
		self._client.on_connect = cb


	def get_plain_topic(self, topic):
		return topic.replace("{}/".format(self._config['topic']), "")


	def subscribe(self, topic):
		topic = "{}/{}".format(self._config['topic'], topic)
		logging.info("Subscribing to topic: {0}".format(topic))
		self._client.subscribe(topic)


	def publish(self, topic, payload):
		topic = "{}/{}".format(self._config['topic'], topic)
		logging.info("Publish %s: %s, %s, %s", topic, payload, self._config["qos"], self._config["retain"])
		try:
			self._client.publish(topic, payload, self._config["qos"], self._config["retain"])
		except Exception as e:
			logging.error(traceback.format_exc())


	def run(self):
		self._client.connect(self._config['host'], self._config['port'])
		self._client.loop_start()
