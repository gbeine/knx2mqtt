import unittest

from unittest.mock import MagicMock
from unittest.mock import ANY

from xknx.dpt import DPTArray
from xknx.dpt.dpt_2byte_float import DPTTemperature
from knx2mqtt.knx import KNX
from knx2mqtt.config import Item


class TestKnx(unittest.TestCase):
    def test_knx_init(self):
        knx_config = [
            Item({
                'address': '1/0/0',
                'type': 'DPTTemperature'
            }),
            Item({
                'address': '1/0/1',
                'type': 'DPTTemperature'
            })
        ]
        k = KNX(knx_config)
        self.assertEqual(2, len(k._subscription_addresses))
        self.assertIn('1/0/0', k._subscription_addresses)
        self.assertIn('1/0/1', k._subscription_addresses)


    def test_knx_publish(self):
        knx_config = [
            Item({
                'address': '1/0/0',
                'type': 'DPTTemperature',
                'knx_publish': 'true'
            }),
            Item({
                'address': '1/0/1',
                'type': 'DPTTemperature'
            })
        ]
        k = KNX(knx_config)
        k.publish_value = MagicMock()

        self.assertTrue(k.publish('1/0/0', '22.5'))
        self.assertFalse(k.publish('1/0/1', '23.5'))
        k.publish_value.assert_called_with('1/0/0', ANY)

        calls = k.publish_value.call_args_list
        self.assertEqual('<DPTArray value="[0xc,0x65]" />', str(calls[0][0][1]))


    def test_knx_publish_value(self):
        k = KNX([])
        k.connect()
        k._xknx.telegrams.put = MagicMock()

        dpt_value = DPTArray(DPTTemperature.to_knx('23.5'))
        k.publish_value('4/2/1', dpt_value)

        k._xknx.telegrams.put.assert_called_with(ANY)

        calls = k._xknx.telegrams.put.call_args_list
        expected = '<Telegram direction="Outgoing" source_address="0.0.0" destination_address="4/2/1" payload="<DPTArray value="[0xc,0x97]" />" />'
        self.assertEqual(expected, str(calls[0][0][0]))



if __name__ == '__main__':
    unittest.main()
