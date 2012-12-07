'''
Created on Dec 2, 2012

@author: mazzzy
'''
import gtk
from RP.gui import gui
import logging


if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    gui_instance = gui()
    gui_instance.pcap_file = "../../medienkomm"
    gui_instance.main.show()
    gtk.main()
    gui_instance.start_parsing(None)