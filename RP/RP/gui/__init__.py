import sys
import gtk
from RP import reader
from pprint import pprint 

class gui:

    def __init__( self ):
        builder = gtk.Builder()
        builder.add_from_file("main.glade") 
        builder.connect_signals(self)
        self.window = builder.get_object("main")
        self.output_window = builder.get_object("output_window")
        self.file_chooser = builder.get_object("filechooserdialog")
        self.statusbar = builder.get_object("statusbar")
        self.statusbar.push(0, "No file chosen yet...")
        self.about = builder.get_object("aboutdialog")
        self.about.set_version("version")
        self.ip_list = builder.get_object("liststore")
        self.ip_list.append(["blah!"])
        
    def open_file(self, widget):
        self.file_chooser.show()
        blah = self.output_window.get_buffer()
        blah.set_text("123")
        
    def start_parsing(self, widget):
        try:
            reader.start_parsing(self.pcap_file)
                
        except:
            self.statusbar.push(3, "no file chosen! aborting")
            raise 
            
    def file_chosen(self, widget):
        self.pcap_file = self.file_chooser.get_filename()
        self.file_chooser.hide()
        self.statusbar.push(1, "Active file: " + self.pcap_file)

    def select_ip(self, widget):
        (model, iter) = widget.get_selected()
        value = model.get_value(iter, 0)
        self.output_window.get_buffer().insert_at_cursor(value + "\n")
        
    def file_cancel(self, widget):
        self.file_chooser.hide()
        
    def print_gui(self, widget):
        print "blub"

    def quit(self, widget):
        gtk.main_quit()
        print "Cleaning up .."
        #TODO: cleanup
        sys.exit(1)
        
    def about_open(self, widget):
        self.about.show()
        
    def about_close(self, widget, data):
        self.about.hide()
    
if __name__ == "__main__":
    gui_instance = gui()

    gui_instance.window.show()
    gtk.main()

