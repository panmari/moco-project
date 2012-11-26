import sys
import gtk
import RP

class gui:

    def __init__( self ):
        builder = gtk.Builder()
        builder.add_from_file("main.glade") 
        builder.connect_signals(self)
        self.window = builder.get_object("main")
        self.output_window = builder.get_object("output_window")
        
    def open_file(self, widget):
        self.output_window.insert "blah"
    
    def print_gui(self, widget):
        print "blub"

    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()
    
if __name__ == "__main__":
    gui_instance = gui()

    gui_instance.window.show()
    gtk.main()

