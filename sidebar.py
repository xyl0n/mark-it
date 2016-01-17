#!/usr/bin/env python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

from filemanager import MarkItFileManager
from textview import MarkItTextView

class MarkItSidebar (Gtk.Box):
    # A class which handles the sidebar used to switch and present files

    __gsignals__ = {
        'row-clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }

    def __init__ (self, files):
        Gtk.Box.__init__ (self)

        self.file_manager = files
        self.set_orientation (Gtk.Orientation.VERTICAL)
        self.set_size_request (200, -1)

        self.file_manager.connect ('file-added', self.on_file_added)
        self.get_style_context ().add_class ("markit-sidebar");
        self.get_style_context ().add_class ("view");
        self.get_style_context ().add_class ("sidebar");

        self.file_stack = Gtk.Stack ()

        self.setup_file_browser ()

        if len(self.file_manager.get_file_list()) == 0:
            self.file_manager.create_new_file ()

    def get_stack (self):
        return self.file_stack

    def setup_file_browser (self):
        doc_label = Gtk.Label ("<b>Documents</b>")
        doc_label.set_use_markup (True)
        doc_label.get_style_context().add_class ("dim-label")
        doc_label.set_alignment (0.0, 0.5)
        doc_label.set_margin_left (12)

        self.pack_start (doc_label, False, False, 6)

        self.file_listbox = Gtk.ListBox ()
        self.file_listbox.connect ('row_activated',
            lambda listbox, row:
                self.emit ("row-clicked", row.get_children ()[0].get_text ())
            )
        self.populate_sidebar ()

        self.pack_start (self.file_listbox, True, True, 0)

    def populate_sidebar (self):
        for file_object in self.file_manager.get_file_list ():
            file_label = self.create_sidebar_row (self.file_manager.path_to_name (file_object.name))
            row = Gtk.ListBoxRow ()
            row.add (file_label)
            self.file_listbox.insert (row, -1)

        self.file_listbox.show_all ()

    def create_sidebar_row (self, label):
        file_label = Gtk.Label (label)
        file_label.set_alignment (0.0, 0.5)
        file_label.set_margin_left (16)
        return file_label

    def remove_children (self):
        children = self.file_listbox.get_children ()
        for child in children:
            child.destroy ()

    def on_file_added (self, *args):
        # Insert a new entry on sidebar for the file
        new_file_label = self.create_sidebar_row (args[1])
        index = self.file_manager.get_index_of_file (args[1])
        self.file_listbox.insert (new_file_label, index)
        self.file_listbox.show_all ()

        text_view = MarkItTextView (self.file_manager.get_file_object_from_name (args[1]))
        text_scrolled = Gtk.ScrolledWindow ()
        text_scrolled.add (text_view)

        self.file_stack.add_named (text_scrolled, args[1])
        self.file_stack.set_visible_child_name (args[1])
