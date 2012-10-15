from scapy.all import *
import re
from socket import gethostbyaddr

GET = re.compile('GET (.*) .*')

def is_http(pkg):
    if not pkg.haslayer(TCP): return False
    tcp_pkg = pkg[TCP]
    if not (tcp_pkg.dport == 80 or tcp_pkg.sport == 80): return False
    if isinstance(tcp_pkg.payload, NoPayload): return False
    return True

def print_http(pkg):
    if not pkg.haslayer(TCP): 
        print "Package has no TCP layer:"
        print pkg.summary()
    tcp_pkg = pkg[TCP]
    match = GET.match(str(tcp_pkg.payload))
    if match:
        try:
            url = gethostbyaddr(pkg[IP].dst)[0]
            print "http://{}/{}".format(url, match.group(1))
        except:
            print "http://{}/{}".format(str(pkg[IP].dst), match.group(1))


class PcapEvents(object):
    "Calls observers if their predicate applies to a package from the stream"
    def __init__(self, reader):
        self._reader = reader
        self._observers = {}

    def __setitem__(self, filter, callback):
        "sets a callback, if the given filter applies to a package"
        self._observers[filter] = callback

    def next(self):
        pkg = next(self._reader)
        for filter, callback in self._observers.items():
            if filter(pkg):
                callback(pkg)
        return pkg

    def __iter__(self):
        return self

def puts(arg):
    print(arg)

if '__main__' == __name__:
    import sys, os.path
    path = os.path.expanduser(sys.argv[1])
    print "Starting on {}".format(path)
    pcap_file = PcapReader(path)
    evts = PcapEvents(pcap_file)
    evts[is_http] = print_http
    for i,pkg in enumerate(evts):
        pass
