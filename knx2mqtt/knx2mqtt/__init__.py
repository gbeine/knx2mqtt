
from knx2mqtt.config import Config
from knx2mqtt.daemon import Daemon
from knx2mqtt.options import Options


def main():
	options = Options()
	cfg = Config()
	cfg.read(options.config())
	d = Daemon(cfg)
	d.run()


main()
