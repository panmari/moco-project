from __future__ import print_function
from scapy.all import PcapReader, TCP, NoPayload, IP
import re
from pykka.actor import ThreadingActor
from pykka.registry import ActorRegistry

GET = re.compile('GET (.*) .*')


class HttpHandler(ThreadingActor):
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
            print("http://{}/{}".format(str(pkg[IP].dst), match.group(1)))


class PcapEvents(ThreadingActor):
    "Calls observers if their predicate applies to a package from the stream"
    def __init__(self, reader):
        ThreadingActor.__init__(self)
        self._reader = reader
        self._observers = {}

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
            self.next()
            self.actor_ref.proxy().all_packages()
        except StopIteration:
            self.stop()

if '__main__' == __name__:
    from signal import signal, SIGINT
    import sys, os.path
    from time import sleep
    import logging
    logging.basicConfig()
    logging.getLogger('pykka').setLevel(logging.DEBUG)
    def stop(*args):
        print("STOPPING")
        ActorRegistry.stop_all()
        sys.exit()
    signal(SIGINT, stop)

    path = os.path.expanduser(sys.argv[1])
    print("# Starting on {}".format(path))
    pcap_file = PcapReader(path)
    evts = PcapEvents.start(pcap_file)
    http = HttpHandler.start().proxy()
    evts.proxy().handler(http.accept, http.print)
    evts.proxy().all_packages()
    while evts.is_alive():
        sleep(0.1)
    ActorRegistry.stop_all()
    sys.exit()
