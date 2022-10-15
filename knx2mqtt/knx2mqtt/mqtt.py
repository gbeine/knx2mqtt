import traceback
import logging
import time
import json

import paho.mqtt.client as mqtt

class MQTT:

	def __init__(self, config, items):
		self._config = config
		self._subscription_topics = [] # this list contains all the topics to subscribe
		self._publishing_topics = [] # this list contains all the topics to publish
		self._published_values = {} # this dict contains the last value published to a certain address
		self._configured_items = {} # configured items
		self._topic_address_map = {} # map mqtt subscription topics to item addresses
		for item in items:
			if item.mqtt_publish():
				self._add_item_to_publish(item)
			if item.mqtt_subscribe():
				self._add_item_to_subscribe(item)


	def connect(self):
		self._client = mqtt.Client()
		if self._config['user'] and self._config['password']:
			self._client.username_pw_set(self._config['user'], self._config['password'])
		self._client.on_connect = self._on_connect


	def disconnect(self):
		self.client.disconnect()


	def set_message_cb(self, cb):
		"""Set the callback method to be used when a MQTT message arrives"""
		self._client.on_message = self._on_message(cb)


	def get_plain_topic(self, topic):
		"""Removes the global part from an MQTT topic"""
		return topic.replace("{0}/".format(self._config['topic']), "")


	def publish(self, topic, payload):
		"""Publish a certain payload"""
		logging.debug("Try to publish payload {0} for topic {1}".format(payload, topic))

		if topic not in self._publishing_topics:
			logging.info("Publish to topic {0} is not allowed".format(topic))
			return

		if topic in self._published_values and self._published_values[topic] == payload:
			logging.debug("Current value for topic {0} did not change, will not publish".format(topic))
			# maybe allowing to force publishing should be an option?
			return False

		topics = [ "{0}/{1}".format(self._config['topic'], topic) ]
		if topic in self._configured_items:
			topics.extend(self._configured_items[topic].mqtt_topics())

		for current_topic in topics:
			self._publish_value(current_topic, payload)
			self._published_values[current_topic] = payload

		return True


	def run(self):
		self._client.connect(self._config['host'], self._config['port'])
		self._client.loop_start()


	def _on_connect(self, client, userdata, flags, rc):
		"""Subscribe to all MQTT topics when connection is established"""
		try:
			logging.info("MQTT connection callback")

			for topic in self._subscription_topics:
				self._subscribe(topic)

		except Exception as e:
			logging.error(traceback.format_exc())

		return True


	def _on_message(self, cb):
		def on_message(client, userdata, message):
			try:
				logging.debug("MQTT connection callback")
				topic = message.topic
				payload = str(message.payload.decode())  # ensure that payload is string

				logging.debug("Message {0} from topic {1}".format(payload, topic))

				if self._config['json']:
					value = self._parse_value_from_json(payload)
				else:
					value = payload

				# publish value to the default KNX address of the topic's item
				address = self._topic_address_map[topic]
				cb(address, value)

			except Exception as e:
				logging.error(traceback.format_exc())

			return True
		return on_message

	def _subscribe(self, topic):
		"""Subscribe to a certain MQTT topic"""
		logging.info("Subscribing to topic: {0}".format(topic))
		self._client.subscribe(topic)


	def _publish_value(self, topic, payload):
		"""Publish a payload to a certain MQTT topic"""
		logging.debug("Publish %s: %s, %s, %s", topic, payload, self._config['qos'], self._config['retain'])
		if self._config['json']:
			message = json.dumps({
				'timestamp': int(time.time()),
				'value': payload
			})
		else:
			message = payload
		try:
			self._client.publish(topic, message, self._config['qos'], self._config['retain'])
		except Exception as e:
			logging.error(traceback.format_exc())


	def _parse_value_from_json(self, payload):
		"""Wraps around the callback method in case the payload is expected as JSON."""
		msg = json.loads(payload)
		if not 'value' in msg:
			raise ValueError('No value attribute in message payload')
		return msg['value']


	def _add_item_to_publish(self, item):
		self._publishing_topics.append(item.address())
		self._published_values[item.address()] = None
		self._configured_items[item.address()] = item
		for topic in item.mqtt_topics():
			self._publishing_topics.append(topic)
			self._published_values[topic] = None


	def _add_item_to_subscribe(self, item):
		address = item.address()
		topic = "{0}/{1}".format(self._config['topic'], address)
		self._subscription_topics.append(topic)
		self._topic_address_map[topic] = address
		self._configured_items[address] = item
		for topic in item.mqtt_topics():
			self._subscription_topics.append(topic)
			self._topic_address_map[topic] = address
