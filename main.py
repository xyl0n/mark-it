#!/usr/bin/env python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango

from textview import MarkItTextView
from sidebar import MarkItSidebar
from filemanager import MarkItFileManager
from stack import MarkItStack

import threading

class MarkItWindow(Gtk.Window):

    def __init__ (self):
        Gtk.Window.__init__(self)
        self.set_title ("Mark It")
        self.set_default_size (1200, 800)
        self.connect ("delete-event", self.on_close)

        self.file_manager = MarkItFileManager ()

        self.create_interface ()

    def create_interface (self):

        # Make the headerbar
        self.header = Gtk.HeaderBar ()
        self.header.set_title ("Untitled 1")
        self.header.set_show_close_button (True)
        self.set_titlebar (self.header)

        self.new_file_button = Gtk.Button ().new_from_icon_name ("document-new-symbolic", 1)
        self.new_file_button.connect ('clicked', self.create_new_file)
        self.header.pack_start (self.new_file_button)

        self.box = Gtk.Box ()
        self.paned = Gtk.Paned ()

        self.sidebar = MarkItSidebar (self.file_manager)
        self.sidebar.connect ("row-clicked", self.on_row_clicked)
        self.paned.add1 (self.sidebar)

        self.stack = MarkItStack (self.file_manager)
        self.stack.show_all ()

        self.paned.add2 (self.stack)
        self.box.pack_start (self.paned, True, True, 0)

        self.add (self.box)

    # Wrapper function
    def create_new_file (self, *args):
        self.file_manager.create_new_file ()

    def on_row_clicked (self, *args):
        self.stack.set_visible_child_name (args[1])
        self.header.set_title (args[1])

    def on_close (self, *args):
        for file_object in self.file_manager.get_file_list ():
            while threading.activeCount() > 1:
                pass
            else:
                file_object.close ()

window = MarkItWindow ()
window.connect('delete-event', Gtk.main_quit)
window.show_all ()
Gtk.main ()
