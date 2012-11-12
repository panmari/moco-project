
#!/usr/bin/env python
import RP
import argparse
from RP import version
import logging

def listener(name):
    if name.lower() == 'http':
        return RP.HttpHandler()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "TODO")
    parser.add_argument('-V', '--version', action='version', version = '%(prog)s {}'.format(version))
    parser.add_argument('-v', '--verbose', action='store_true')
    #parser.add_argument('-i', '--ip', type = str, default=None) # TODO
    parser.add_argument('-t', '--type', action='append', type = listener, default=[])
    parser.add_argument('file', metavar='FILE', nargs=1)
    args = parser.parse_args()
    events = RP.PcapEvents(args.file[0])
    if args.verbose:
        logging.basicConfig(level = logging.DEBUG)
    else:
        logging.basicConfig(level = logging.INFO)
    for listener in args.type:
        events[listener.accept] = listener.handle
    events.all_packages()
