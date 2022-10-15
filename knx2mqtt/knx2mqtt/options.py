import os.path
import argparse

class Options:
    """Class for parsing knx2mqtt command line options"""


    def __init__(self):
        parser = argparse.ArgumentParser(description='A KNX2MQTT Bridge allowing bidirectional telegram transfer')
        parser.add_argument('-c', '--config', type=str, help='path to a knx2mqtt configuration file')
        parser.add_argument('-l', '--logconfig', type=str, help='path to a logging configuration file')
        args = parser.parse_args()

        if args.config:
            self._config = args.config

        if args.logconfig:
            self._logconfig = args.logconfig


    def config(self):
        if not hasattr(self, '_config'):
            if os.path.exists('/etc/knx2mqtt.yaml'):
                self._config = '/etc/knx2mqtt.yaml'
            else:
                self._config = 'knx2mqtt.yaml'
        return self._config


    def logconfig(self):
        if not hasattr(self, '_logconfig'):
                self._logconfig = 'logging.conf'
        return self._logconfig
