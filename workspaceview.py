#!/usr/bin/evn python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

class MarkItWorkspaceView (Gtk.ListBox):

    __gsignals__ = {
        'file_clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }

    def __init__ (self, file_manager):
        Gtk.ListBox.__init__ (self)

        self.file_manager = file_manager
        self.connect ('row_activated', self.on_row_clicked)
        self.populate ()

    def on_row_clicked (self, listbox, row):
        file_name = row.get_children ()[0].get_text ()
        self.emit ('file_clicked', file_name)

    def populate (self):
        for file_object in self.file_manager.get_file_list ():
            file_label = self.create_row (file_object.get_name ())
            row = Gtk.ListBoxRow ()
            row.add (file_label)
            self.insert (row, -1)

        self.show_all ()

    def create_row (self, label):
        file_label = Gtk.Label (label)
        file_label.set_alignment (0.0, 0.5)
        file_label.set_margin_left (16)
        file_label.get_style_context ().add_class ('markit-sidebar-row')
        return file_label
