import sys
import gtk
import RP
from pprint import pprint 

class gui:

    def __init__( self ):
        builder = gtk.Builder()
        builder.add_from_file("main.glade") 
        builder.connect_signals(self)
        self.window = builder.get_object("main")
        self.output_window = builder.get_object("output_window")
        self.file_chooser = builder.get_object("filechooserdialog")
       # pprint (dir(self.output_window), indent=2)
        
    def open_file(self, widget):
        self.file_chooser.show()
        blah = self.output_window.get_buffer()
        blah.set_text("123")
        
    def start_parsing(self, widget):
        try:
            print "Parsing..."
            #do something with self.pcap_file
        except:
            print "no file chosen! aborting"
            
    def file_chosen(self, widget):
        self.pcap_file = self.file_chooser.get_file
        self.file_chooser.hide()
        
    def file_cancel(self, widget):
        self.file_chooser.hide()
        
    def print_gui(self, widget):
        print "blub"

    def quit(self, widget):
        gtk.main_quit()
        print "Cleaning up .."
        #TODO: cleanup
        sys.exit(1)
    
if __name__ == "__main__":
    gui_instance = gui()

    gui_instance.window.show()
    gtk.main()

