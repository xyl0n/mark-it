#!/usr/bin/evn python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

from filemanager import MarkItFileObject

class MarkItWorkspaceView (Gtk.ListBox):

    __gsignals__ = {
        'file_clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,)), # We use paths to identify files
    }

    def __init__ (self, file_manager):
        Gtk.ListBox.__init__ (self)

        self.file_manager = file_manager
        self.path_row_index = dict () # Since we may have multiple rows with the same name but different paths
        self.populate ()
        self.connect ('row_activated', self.on_row_clicked)

    def on_row_clicked (self, listbox, row):
        file_path = self.path_row_index [row.get_index ()]
        self.emit ('file_clicked', file_path)

    def populate (self):

        if len (self.file_manager.get_open_files ()) == 0:
            print ("NO OPEN FILES")

        for file_object in self.file_manager.get_open_files ():
            self.add_row (file_object)

        self.show_all ()

    def add_row (self, file_object):
        file_label = Gtk.Label (file_object.get_name ())
        file_label.set_alignment (0.0, 0.5)
        file_label.set_margin_left (16)
        file_label.get_style_context ().add_class ('markit-sidebar-row')

        row = Gtk.ListBoxRow ()
        row.add (file_label)
        self.insert (row, -1)
        row_num = row.get_index ()
        self.path_row_index[row_num] = file_object.get_path ()

        self.show_all ()
