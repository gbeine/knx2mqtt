from setuptools import setup
  
setup(name='knx2mqtt',
      version='0.2',
      description='KNX 2 MQTT bridge',
      url='https://github.com/gbeine/knx2mqtt',
      author='Gerrit Beine',
      author_email='mail@gerritbeine.de',
      license='MIT',
      packages=['knx2mqtt'],
      requires=[
          'logging',
          'paho.mqtt',
          'pyyaml',
          'xknx',
        ],
      zip_safe=False)

