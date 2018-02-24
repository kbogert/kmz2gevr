from distutils.core import setup

setup(
	name='kmz2gevr',
	version='1.0',
	author="Kenneth Bogert",
	requires=['pykml', 'googlemaps', 'google', 'libxmp'],
	provides=["kmz2gevr"],
	packages=['kmz2gevr']

	)
