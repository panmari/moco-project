
#!/usr/bin/env python
import RP
import argparse
from RP import version

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = "TODO")
	parser.add_argument('-V', '--version', action='version', version = '%(prog)s {}'.format(version))
	args = parser.parse_args()
