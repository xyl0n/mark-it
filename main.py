#!/usr/bin/env python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, Gdk

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

        style = Gtk.CssProvider ()
        style.load_from_path ("style.css")
        self.get_style_context ().add_provider_for_screen (Gdk.Screen.get_default (),
                                                           style, Gtk.STYLE_PROVIDER_PRIORITY_THEME)

        self.create_interface ()

    def create_interface (self):

        self.set_titlebar (self.create_titlebar ())

        self.box = Gtk.Box ()
        self.paned = Gtk.Paned ()

        self.stack = MarkItStack (self.file_manager)
        self.stack.show_all ()

        self.sidebar = MarkItSidebar (self.file_manager, self.stack)
        self.sidebar.connect ("active_file_changed", self.on_active_file_changed)
        self.paned.add1 (self.sidebar)
        self.document_nav_header.set_size_request (self.sidebar.get_size_request()[0], -1)
        self.sidebar.connect ("size_allocate", self.on_sidebar_size_change)

        self.paned.add2 (self.stack)
        self.box.pack_start (self.paned, True, True, 0)

        self.add (self.box)

    def create_titlebar (self):
        # Make the titlebar
        # This is for document specific actions
        self.right_header = Gtk.HeaderBar ()
        self.right_header.set_title ("Untitled 1")
        self.right_header.set_show_close_button (True)
        self.right_header.get_style_context().add_class("titlebar")
        self.right_header.get_style_context().add_class("markit-right-header")

        # This is for the file browser
        self.document_nav_header = Gtk.HeaderBar ()
        self.document_nav_header.set_show_close_button (False)
        self.document_nav_header.get_style_context().add_class("titlebar")
        self.document_nav_header.get_style_context().add_class("markit-document-header")

        # Make a new file
        new_file_button = Gtk.Button ().new_from_icon_name ("document-new-symbolic", 1)
        new_file_button.connect ('clicked', self.create_new_file)
        self.document_nav_header.pack_start (new_file_button)

        new_folder_button = Gtk.Button ().new_from_icon_name ("folder-new-symbolic", 1)
        new_folder_button.connect ('clicked', self.create_new_folder)
        self.document_nav_header.pack_start (new_folder_button)

        self.header_box = Gtk.Box ()
        self.header_box.pack_start (self.document_nav_header, False, False, 0)
        self.header_box.pack_start (Gtk.Separator.new (Gtk.Orientation.VERTICAL), False, False, 0)
        self.header_box.pack_start (self.right_header, True, True, 0)

        return self.header_box


    # Wrapper function
    def create_new_file (self, *args):
        self.file_manager.create_new_file ()

    def create_new_folder (self, *args):
        # We want to add a new row to the document viewer, except make it a folder
        pass

    def on_active_file_changed (self, *args):
        self.right_header.set_title (args[1])

    def on_sidebar_size_change (self, widget, allocation):
        self.document_nav_header.set_size_request (allocation.width, -1)

    def on_close (self, *args):
        # We don't want to close while some files are still saving
        for file_object in self.file_manager.get_file_list ():
            while threading.activeCount() > 1:
                pass
            else:
                file_object.close ()

window = MarkItWindow ()
window.connect('delete-event', Gtk.main_quit)
window.show_all ()
Gtk.main ()
