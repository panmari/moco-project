import unittest
from scapy.all import PcapReader
from ..reader import PcapEvents, HttpHandler
from .helpers import *

class Test(unittest.TestCase):
    def setUp(self):
        self.file = PcapReader(relative("onlyAck"))

    def testShouldParseEvents(self):
        evts = PcapEvents(self.file)
        #TODO: write some useful test
        #print "" + evts.next()

    def testFirstEventShouldNotBeHTTP(self):
        evts = PcapEvents(self.file)
        http = HttpHandler()
        self.failIf(http.accept(evts.next()))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
