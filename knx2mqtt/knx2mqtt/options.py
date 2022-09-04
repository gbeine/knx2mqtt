import getopt
import os.path
import sys

class Options:
    """Class for parsing knx2mqtt command line options"""


    def __init__(self):
        argv = sys.argv[1:]
        try:
            opts, args = getopt.getopt(argv, 'c:', ['config'])
            self._parse_opts(opts)
        except getopt.GetoptError as err:
            print(err)  # will print something like "option -a not recognized"
            self.usage()
            sys.exit(2)


    def config(self):
        return self._config


    def usage(self):
        print("use knx2mqtt [-c config.yaml]")


    def _parse_opts(self, opts):
        for o, a in opts:
            if o == '-c':
                if os.path.exists(a):
                    self._config = a
                elif os.path.exists('/etc/knx2mqtt.conf'):
                    self._config = '/etc/knx2mqtt.conf'
                else:
                    self._config = 'knx2mqtt.conf'
