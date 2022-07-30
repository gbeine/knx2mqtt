import traceback
import logging
import paho.mqtt.client as mqtt

class MQTT:

	def __init__(self, config, items):
		self._config = config
		self._subscription_topics = [] # this list contains all the topics to subscribe
		self._publishing_topics = [] # this list contains all the topics to publish
		self._published_values = {} # this dict contains the last value published to a certain address
		self._configured_items = {}
		for item in items:
			item_added = False
			if item.mqtt_publish():
				self._add_item_to_publish(item)
				item_added = True
			if item.mqtt_subscribe():
				self._add_item_to_subscribe(item)
				item_added = True
			if item_added:
				self._configured_items[item.address()] = item


	def connect(self):
		self._client = mqtt.Client()
		self._client.username_pw_set(self._config['user'], self._config['password'])
		self._client.on_connect = self._on_connect


	def disconnect(self):
		self.client.disconnect()


	def set_message_cb(self, cb):
		self._client.on_message = cb


	def get_plain_topic(self, topic):
		return topic.replace("{0}/".format(self._config['topic']), "")


	def publish(self, topic, payload):
		topic = "{0}/{1}".format(self._config['topic'], topic)
		logging.info("Publish %s: %s, %s, %s", topic, payload, self._config["qos"], self._config["retain"])
		try:
			self._client.publish(topic, payload, self._config["qos"], self._config["retain"])
		except Exception as e:
			logging.error(traceback.format_exc())


	def run(self):
		self._client.connect(self._config['host'], self._config['port'])
		self._client.loop_start()


	def _on_connect(self, client, userdata, flags, rc):
		try:
			logging.info("MQTT connection callback")

			for topic in self._subscription_topics:
				self._subscribe(topic)

		except Exception as e:
			logging.error(traceback.format_exc())

		return True


	def _subscribe(self, topic):
		topic = "{0}/{1}".format(self._config['topic'], topic)
		logging.info("Subscribing to topic: {0}".format(topic))
		self._client.subscribe(topic)


	def _add_item_to_publish(self, item):
		self._publishing_topics.append(item.address())
		self._published_values[item.address()] = None
		for topic in item.mqtt_topics():
			self._publishing_topics.append(topic)
			self._published_values[topic] = None


	def _add_item_to_subscribe(self, item):
		self._subscription_topics.append(item.address())
		for topic in item.mqtt_topics():
			self._subscription_topics.append(topic)
