'''
Created on Dec 2, 2012

@author: mazzzy
'''
import gtk
from RP.gui import Gui
import logging


if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    gui_instance = Gui()
    gui_instance.main.show()
    gui_instance.pcap_file = "../../medienkomm"
    gui_instance.start_parsing(None)
    gtk.main()
    
