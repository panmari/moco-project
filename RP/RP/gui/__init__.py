import sys
import gtk
import scapy
from RP import reader
from RP import version
from pprint import pprint

class gui:

    def __init__( self ):
        builder = gtk.Builder()
        builder.add_from_file("main.glade") 
        builder.connect_signals(self)
        self.window = builder.get_object("main")
        self.file_chooser = builder.get_object("filechooserdialog")
        self.statusbar = builder.get_object("statusbar")
        self.statusbar.push(0, "No file chosen yet...")
        self.about = builder.get_object("aboutdialog")
        self.about.set_version(version)
        self.packages_treeview = builder.get_object("packages_treeview")
        self.ip_list = builder.get_object("liststore")
        self.ip_list.append(["blah!"])
        
    def open_file(self, widget):
        self.file_chooser.show()
        
    def start_parsing(self, widget):
        try:
            #todo: do this in new thread
            http_handler = reader.start_parsing(self.pcap_file) 
            self.packages_treeview.set_model(http_handler.gtk_list_store)
        except Exception as e:
            self.statusbar.push(3, e[0])
            #raise error for debugging
            raise 
            
    def file_chosen(self, widget):
        self.pcap_file = widget.get_filename()
        widget.hide()
        self.statusbar.push(1, "Active file: " + self.pcap_file)

    def select_ip(self, widget):
        (model, iter) = widget.get_selected()
        value = model.get_value(iter, 0)
        #TODO: get the ListStore for the respective model
        #self.packages_view.set_model(some_model)
        
    def file_cancel(self, widget):
        self.file_chooser.hide()

    def quit(self, widget):
        gtk.main_quit()
        print "Cleaning up .."
        #TODO: cleanup
        sys.exit(1)
        
    def about_open(self, widget):
        self.about.run()
        
    def about_close(self, widget, data=None):
        widget.hide()
    
if __name__ == "__main__":
    gui_instance = gui()

    gui_instance.window.show()
    gtk.main()

