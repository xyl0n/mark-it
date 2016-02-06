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
        self.file_manager.connect ('file_opened', self.on_file_open)

        self.populate ()

        self.show_all ()

    def populate (self):
        for file_obj in self.file_manager.get_open_files ():
            print ("adding: " + file_obj.get_path ())
            self.add_page (file_obj.get_path ())

    def add_page (self, path):
        if self.get_child_by_name (path) == None:
            text_view = MarkItTextView (self.file_manager.get_file_object_from_path (path))
            text_scrolled = Gtk.ScrolledWindow ()
            text_scrolled.add (text_view)

            self.add_named (text_scrolled, path)
            self.set_visible_child_name (path)

            self.show_all ()

    def on_file_open (self, *args):
        self.add_page (args[1])
