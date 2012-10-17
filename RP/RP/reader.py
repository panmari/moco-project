from __future__ import print_function
from scapy.all import PcapReader, TCP, NoPayload, IP
import re
from socket import gethostbyaddr
import functools

GET = re.compile('GET (.*) .*')

def memoize(obj):
    cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = obj(*args, **kwargs)
        return cache[args]
    return memoizer

@memoize
def reverse_dns(ip):
    try:
        return gethostbyaddr(ip)[0]
    except:
        return ip

class HttpHandler(object):
    def accept(self, pkg):
        if not pkg.haslayer(TCP): return False
        tcp_pkg = pkg[TCP]
        if not (tcp_pkg.dport == 80 or tcp_pkg.sport == 80): return False
        if isinstance(tcp_pkg.payload, NoPayload): return False
        return True

    def print(self, pkg):
        if not pkg.haslayer(TCP): 
            print("Package has no TCP layer:")
            print(pkg.summary())
        tcp_pkg = pkg[TCP]
        match = GET.match(str(tcp_pkg.payload))
        if match:
            print("http://{}/{}".format(str(reverse_dns(pkg[IP].dst)), match.group(1)))


class PcapEvents(object):
    "Calls observers if their predicate applies to a package from the stream"
    def __init__(self, reader):
        self._reader = reader
        self._observers = {}

    def __setitem__(self, filter, callback):
        return self.handler(filter, callback)

    def handler(self, filter, callback):
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

    def all_packages(self):
        try:
            while True:
                yield self.next()
        except StopIteration:
            self.stop()

if '__main__' == __name__:
    import sys, os.path

    path = os.path.expanduser(sys.argv[1])
    print("# Starting on {}".format(path))
    pcap_file = PcapReader(path)
    evts = PcapEvents(pcap_file)
    http = HttpHandler()
    evts[http.accept]= http.print
    for pkg in evts.all_packages():
        pass
