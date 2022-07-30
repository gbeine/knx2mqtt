import unittest
from knx2mqtt import config


class TestConfig(unittest.TestCase):

    def test_simple_item(self):
        item_config = {
            'address': '1/0/0',
            'type': 'DPTTemperature'
        }
        item = config.Item(item_config)
        self.assertEqual(item.address(), '1/0/0')
        self.assertEqual(item.type(), 'DPTTemperature')
        self.assertFalse(item.mqtt_subscribe())
        self.assertTrue(item.mqtt_publish())
        self.assertTrue(item.knx_subscribe())
        self.assertFalse(item.knx_publish())

    def test_change_mqtt_subscribe(self):
        item_config = {
            'address': '1/0/0',
            'type': 'DPTTemperature',
            'mqtt_subscribe': True
        }
        item = config.Item(item_config)
        self.assertTrue(item.mqtt_subscribe())
        self.assertTrue(item.mqtt_publish())
        self.assertTrue(item.knx_subscribe())
        self.assertFalse(item.knx_publish())

    def test_change_mqtt_publish(self):
        item_config = {
            'address': '1/0/0',
            'type': 'DPTTemperature',
            'mqtt_publish': False
        }
        item = config.Item(item_config)
        self.assertFalse(item.mqtt_subscribe())
        self.assertFalse(item.mqtt_publish())
        self.assertTrue(item.knx_subscribe())
        self.assertFalse(item.knx_publish())

    def test_change_knx_subscribe(self):
        item_config = {
            'address': '1/0/0',
            'type': 'DPTTemperature',
            'knx_subscribe': False
        }
        item = config.Item(item_config)
        self.assertFalse(item.mqtt_subscribe())
        self.assertTrue(item.mqtt_publish())
        self.assertFalse(item.knx_subscribe())
        self.assertFalse(item.knx_publish())

    def test_change_knx_publish(self):
        item_config = {
            'address': '1/0/0',
            'type': 'DPTTemperature',
            'knx_publish': True
        }
        item = config.Item(item_config)
        self.assertFalse(item.mqtt_subscribe())
        self.assertTrue(item.mqtt_publish())
        self.assertTrue(item.knx_subscribe())
        self.assertTrue(item.knx_publish())

    def test_require_address(self):
        item_config = {
            'type': 'DPTTemperature'
        }
        with self.assertRaises(ValueError):
            item = config.Item(item_config)

    def test_require_type(self):
        item_config = {
            'address': '1/0/0'
        }
        with self.assertRaises(ValueError):
            item = config.Item(item_config)

    def test_full_config(self):
        c = config.Config()
        c.read('test_config.yaml')
        self.assertEqual(len(c.knx()), 8)


if __name__ == '__main__':
    unittest.main()
