from __future__ import print_function
from scapy.all import PcapReader, TCP, NoPayload, IP
import re
from socket import gethostbyaddr
from helpers import memoize, do
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import logging
logger = logging.getLogger('Reader')

GET = re.compile('GET (.*) .*')

_dns_thread_pool = ThreadPoolExecutor(max_workers=50)

@memoize
def reverse_dns(ip):
    logger.debug("Started rdns for %s", ip)
    def lookup():
        try:
            return gethostbyaddr(ip)[0]
        except:
            return ip
    return _dns_thread_pool.submit(lookup)

class HttpHandler(object):
    """Has callbacks that are invoked by the event system.

    It only accepts packets if:
        * They are HTTP GET requests
        * send or received by the IP given. If none is given, every
          IP is accepted.
    
    Subclass and overwrite handle for great good."""
    def __init__(self, ip = None):
        self.ip = ip

    def accept(self, pkg):
        logger.debug("Accepting? %s", pkg.summary())
        if not pkg.haslayer(TCP): return False
        tcp_pkg = pkg[TCP]
        if not (tcp_pkg.dport == 80 or tcp_pkg.sport == 80): return False
        if isinstance(tcp_pkg.payload, NoPayload): return False
        if self.ip is not None: 
            return pkg[IP].src == self.ip or pkg[IP].dst == self.ip
        else:
            return True
    def handle(self, pkg):
        self.print(pkg)

    def print(self, pkg):
        logger.debug("got a package %s to print", pkg)
        tcp_pkg = pkg[TCP]
        server_name = reverse_dns(pkg[IP].dst)
        match = GET.match(str(tcp_pkg.payload))
        if match:
            try:
                logger.info("http://{}/{}".format(str(server_name.result(5.0)), match.group(1)))
            except TimeoutError:
                logger.info("http://{}/{}".format(str(pkg[IP].dst), match.group(1)))


class PcapEvents(object):
    """Calls observers if their predicate applies to a package from the stream.
    Thread-safeish. Only iterate at one location."""
    def __init__(self, reader):
        if isinstance(reader, str):
            reader = PcapReader(reader)
        self._reader = reader
        self._observers = {}

    def __setitem__(self, filter, callback):
        return self.handler(filter, callback)

    def handler(self, filter, callback):
        "sets a callback, if the given filter applies to a package"
        self._observers[filter] = (callback)

    def next(self):
        "Processes the next package and yields it"
        pkg = next(self._reader)
        def do_callback(tuple):
            logger.debug("Doing callback for %s", tuple)
            filter, callback = tuple
            if filter(pkg):
                try:
                    callback(pkg)
                except Exception as e:
                    logger.warn("Callback failed: %s : %s",
                            e.__class__.__name__, e)
            else:
                logger.debug("Rejected")
        logger.debug("Thread pool executing observer notify")
        with ThreadPoolExecutor(max_workers=3) as e:
            do(e.map(do_callback, self._observers.items()))
        return pkg

    def __iter__(self):
        return self

    def all_packages(self):
        do(self)

if '__main__' == __name__:
    logging.basicConfig(level = logging.INFO)
    import sys, os.path
    try:
        path = os.path.expanduser(sys.argv[1])
    except IndexError:
        print("No file was given as argument, terminating")
        sys.exit()
    path = os.path.expanduser(sys.argv[1])
    logger.info("# Starting on {}".format(path))
    pcap_file = PcapReader(path)
    evts = PcapEvents(pcap_file)
    http = HttpHandler()
    evts[http.accept]= http.print
    evts.all_packages()
