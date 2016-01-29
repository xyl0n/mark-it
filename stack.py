#!/usr/bin/env python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

from textview import MarkItTextView
from filemanager import MarkItFileManager

class MarkItStack (Gtk.Stack):

    def __init__ (self, files):
        Gtk.Stack.__init__ (self)

        self.set_homogeneous(True)
        self.set_transition_type (Gtk.StackTransitionType.CROSSFADE)
        self.set_transition_duration (100)

        self.file_manager = files
        self.file_manager.connect ('file-added', self.on_file_added)

        self.setup_pages ()

        self.show_all ()

    def setup_pages (self):
        for file_object in self.file_manager.get_file_list ():
            self.add_page (file_object.get_name ())

    def add_page (self, name):
        text_view = MarkItTextView (self.file_manager.get_file_object_from_name (name))
        text_scrolled = Gtk.ScrolledWindow ()
        text_scrolled.add (text_view)

        self.add_named (text_scrolled, name)
        self.set_visible_child_name (name)

        self.show_all ()

    def on_file_added (self, *args):
        self.add_page (args[1])

    def join_threads (self):
        for scrolled_child in self.get_children ():
            # This should give us the scrolled window
            for text_view in scrolled_child.get_children ():
                text_view.join_thread ()
