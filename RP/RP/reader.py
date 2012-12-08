from __future__ import print_function
from scapy.all import PcapReader, TCP, NoPayload, IP, sniff
import re
from socket import gethostbyaddr
from helpers import memoize, do
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from threading import Thread
from gtk import ListStore
from datetime import datetime
import gobject

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
        * They are HTTP requests
        * send or received by the IP given. If none is given, every
          IP is accepted.
    
    Subclass and overwrite handle for great good."""
    def __init__(self, ip = None):
        self.ip = ip
        self.gtk_list_store = ListStore(str, str)

    def accept(self, pkg):
        logger.debug("Accepting? %s", pkg.summary())
        if not pkg.haslayer(TCP): return False
        tcp_pkg = pkg[TCP]
        if not (tcp_pkg.dport == 80 or tcp_pkg.sport == 80): return False
        if isinstance(tcp_pkg.payload, NoPayload): return False
        if not GET.match(str(tcp_pkg.payload)): return False
        if self.ip is not None: 
            return pkg[IP].src == self.ip or pkg[IP].dst == self.ip
        else:
            return True
    def handle(self, pkg):
        self.print(pkg)

    def print(self, pkg):
        logger.debug("got a package %s to print", pkg.summary())
        time = datetime.fromtimestamp(pkg.time)
        logger.debug("initially at time={}".format(time))
        tcp_pkg = pkg[TCP]
        server_name = reverse_dns(pkg[IP].dst)
        match = GET.match(str(tcp_pkg.payload))
        try:
            entry = "http://{}{}".format(str(server_name.result(5.0)), match.group(1))
        except TimeoutError:
            entry = "http://{}{}".format(str(pkg[IP].dst), match.group(1))
        logger.info(entry)
        self.gtk_list_store.append([str(time), entry])

class QueenHandler(HttpHandler):
    def __init__(self):
        HttpHandler.__init__(self)
        self.children = {}
        self.ip_callbacks = []
    def handle(self, pkg):
        server_name = reverse_dns(pkg[IP].dst)
        logger.debug("got a package %s to print", pkg.summary())
        time = datetime.fromtimestamp(pkg.time)
        logger.debug("initially at time={}".format(time))
        tcp_pkg = pkg[TCP]
        if pkg[IP].src not in self.children:
            self.children[pkg[IP].src] = HttpHandler(pkg[IP].src)
            for f in self.ip_callbacks:
                f(pkg[IP].src)
        self.children[pkg[IP].src].handle(pkg)
        match = GET.match(str(tcp_pkg.payload))
        try:
            entry = "http://{}{}".format(str(server_name.result(5.0)), match.group(1))
        except TimeoutError:
            entry = "http://{}{}".format(str(pkg[IP].dst), match.group(1))
        logger.info(entry)
        self.gtk_list_store.append([str(time), entry])
    def on_new_ip(self, callback):
        self.ip_callbacks.append(callback)

    def list_store_for(self, ip):
        self.children[ip].gtk_list_store


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

    def handle_packet(self, pkg):
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

    def next(self):
        "Processes the next package and yields it"
        pkg = next(self._reader)
        return self.handle_packet(pkg)

    def __iter__(self):
        return self

    def all_packages(self):
        do(self)

    def setup_sniffer(self):
        sniff(prn=self.handle_packet, filter="tcp", store=0)

def start_parsing(path):
    pcap_file = PcapReader(path)
    evts = PcapEvents(pcap_file)
    http = QueenHandler()
    evts[http.accept]= http.handle
    thread = Thread(target=evts.all_packages)
    thread.daemon = True
    return (http, thread)
    
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
    start_parsing(path)
