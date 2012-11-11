
import unittest
from scapy.all import PcapReader
from RP.reader import PcapEvents, HttpHandler

class Test(unittest.TestCase):


    def setUp(self):
        self.file = PcapReader("../onlyIEEEorgaPackets.pcap")

    def testShouldParseEvents(self):
        evts = PcapEvents(self.file)
        print evts.next()

    def testFirstEventShouldNotBeHTTP(self):
        evts = PcapEvents(self.file)
        http = HttpHandler()
        self.failIf(http.accept(evts.next()))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()