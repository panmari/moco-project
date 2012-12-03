'''
Created on Dec 2, 2012

@author: mazzzy
'''
import unittest
import gtk
from RP.gui import gui

class Test(unittest.TestCase):


    def setUp(self):
        self.gui_instance = gui()
        self.gui_instance.pcap_file = "../../medienkomm"
        self.gui_instance.main.show()
        gtk.main()

    def tearDown(self):
        pass


    def testName(self):
        #todo: make some fake widget with file assigned?
        self.gui_instance.file_chosen(None)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()