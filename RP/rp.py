
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
    parser.add_argument('-s', '--sniff', action='store_true')
    parser.add_argument('-i', '--ip', type = str, default=None, 
            help='Currently the same for all listeners')
    parser.add_argument('-t', '--type', action='append', type = listener,
            default=[], help = "Supported: http")
    parser.add_argument('file', metavar='FILE', nargs='?')
    parser.add_argument('-g', '--gui', action='store_true')
    args = parser.parse_args()
    events = RP.PcapEvents(args.file)
    if args.verbose:
        logging.basicConfig(level = logging.DEBUG)
    else:
        logging.basicConfig(level = logging.INFO)
    if args.gui:
        import gtk
        gui = RP.gui.Gui()
        gui.main.show()
        gtk.main()
    for listener in args.type:
        listener.ip = args.ip
        events[listener.accept] = listener.handle
    if args.sniff:
        events.setup_sniffer()
    else:
        events.all_packages()
