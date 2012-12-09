import sys
import gtk
import os.path
from .. import reader
from .. import version
import logging

gtk.gdk.threads_init()
class Gui:
    gui_logger = logging.getLogger("Gui")

    def __init__( self ):
        builder = gtk.Builder()
        builder.add_from_file(os.path.join(os.path.dirname(__file__), "main.glade")) 
        builder.connect_signals(self)
        self.main = builder.get_object("main")
        self.file_chooser = builder.get_object("filechooserdialog")
        self.statusbar = builder.get_object("statusbar")
        self.statusbar.push(0, "No file chosen yet...")
        self.about = builder.get_object("aboutdialog")
        self.about.set_version(version)
        self.packages_treeview = builder.get_object("packages_treeview")
        self.ip_list = builder.get_object("liststore")
        
    def open_file(self, widget):
        self.file_chooser.show()
        
    def start_parsing(self, widget):
        try:
            self.gui_logger.debug("start parsing on {}".format(self.pcap_file))
            self.http_handler, thread = reader.start_parsing(self.pcap_file) 
            self.packages_treeview.set_model(self.http_handler.gtk_list_store)
            self.http_handler.on_new_ip(self.new_ip)
            thread.start()
        except Exception as e:
            self.statusbar.push(3, str(e))
            self.gui_logger.warn(str(e))
            raise e

    def on_ip_activated(self, widget, *args):
        self.select_ip(widget)
        

    def new_ip(self, ip):
        self.gui_logger.info("New IP: {}".format(ip))
        self.ip_list.append([ip])
    
    def file_chosen(self, widget):
        self.pcap_file = widget.get_filename()
        widget.hide()
        self.gui_logger.info("Reading {}".format(self.pcap_file))
        self.statusbar.push(1, "Active file: " + self.pcap_file)

    def select_ip(self, widget):
        (model, iter) = widget.get_selection().get_selected()
        value = model.get_value(iter, 0)
        self.gui_logger.debug("Model {} chosen -- value {}".format(model, value))
        if value == "ALL":
            self.gui_logger.debug("Show ALL")
            list_store = self.http_handler.gtk_list_store
            self.gui_logger.debug("List store: {}".format(list_store))
            self.packages_treeview.set_model(list_store)
        else:
            self.gui_logger.debug("Show {}".format(value))
            self.packages_treeview.set_model(self.http_handler.list_store_for(value))

        #TODO: get the ListStore for the respective model
        #self.packages_view.set_model(some_model)
        
    def file_cancel(self, widget):
        self.file_chooser.hide()

    def quit(self, widget):
        gtk.main_quit()
        self.gui_logger.debug("Cleaning up ..")
        #TODO: cleanup
        sys.exit(1)
        
    def about_open(self, widget):
        self.about.run()
        
    def about_close(self, widget, data=None):
        widget.hide()
    
if __name__ == "__main__":
    gui_instance = Gui()
    gui_instance.main.show()
    gtk.main()

