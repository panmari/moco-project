
from setuptools import setup
from RP import version

setup(
	name = 'Rainbow Puke',
	version = version,
	description = 'TODO',
	author = "Stefan Moser, Aaron Karper",
	author_email = "None",
	scripts = ['rp.py'],
	packages = ['RP'],
	install_requires = ["setuptools", 'scapy', 'pykka'])
