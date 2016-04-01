#!/usr/bin/env python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, Gdk

from textview import MarkItTextView
from sidebar import MarkItSidebar
from filemanager import MarkItFileManager
from stack import MarkItStack
from dialogmanager import MarkItDialogManager
from titlebar import MarkItTitleBar

import threading

class MarkItWindow (Gtk.Window):

    def __init__ (self):
        Gtk.Window.__init__(self)
        self.set_title ("Mark It")
        self.set_default_size (1200, 800)
        self.set_icon_name ("accessories-text-editor")
        self.connect ("delete-event", self.on_close)

        self.load_settings ()

        self.file_manager = MarkItFileManager (self.opened_files)

        self.dialog_manager = MarkItDialogManager (self)

        self.dialog_manager.connect ('name_dialog_response', self.on_name_dialog_responded)
        self.dialog_manager.connect ('name_dialog_canceled', self.on_name_dialog_cancel)

        style = Gtk.CssProvider ()
        style.load_from_path ("style.css")
        self.get_style_context ().add_provider_for_screen (Gdk.Screen.get_default (),
                                                           style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.create_interface ()

        self.show_all ()

        self.sidebar.hide_widgets ()
        self.sidebar.hide_widgets ()

    def load_settings (self):
        self.app_settings = Gio.Settings.new ("org.gnome.mark-it.saved-state")
        self.opened_files = list ()

        for file_path in self.app_settings.get_strv("opened-files"):
            if file_path != '':
                self.opened_files.append (file_path)

    def create_interface (self):

        self.titlebar = MarkItTitleBar (self.file_manager)
        self.titlebar.connect ('file_create_requested', self.on_file_create_request)
        self.titlebar.connect ('folder_create_requested', self.on_folder_create_request)
        self.set_titlebar (self.titlebar)

        self.box = Gtk.Box ()
        self.paned = Gtk.Paned ()

        self.stack = MarkItStack (self.file_manager)
        self.stack.show_all ()

        self.sidebar = MarkItSidebar (self.file_manager, self.stack, self.dialog_manager)
        self.sidebar.connect ("active_file_changed", self.on_active_file_changed)
        self.paned.add1 (self.sidebar)
        self.titlebar.set_left_header_width (self.sidebar.get_size_request()[0])
        self.sidebar.connect ("size_allocate", self.on_sidebar_size_change)

        self.paned.add2 (self.stack)
        self.box.pack_start (self.paned, True, True, 0)

        self.add (self.box)

    def on_file_create_request (self, *args):
        self.file_manager.create_new_file ()

    def on_folder_create_request (self, *args):
        # We want to add a new row to the document viewer, except make it a folder
        # Lets make a dialog to get the name of the folder
        # TODO: Replace "Untitled Folder" with something else if it already exists
        self.dialog_manager.create_name_dialog ("Create New Folder", "Create", "Untitled Folder", 1)

    def on_name_dialog_responded (self, *args):
        self.file_manager.create_new_folder (args[1])
        self.dialog_manager.destroy_dialog (args[2])

    def on_name_dialog_cancel (self, *args):
        self.dialog_manager.destroy_dialog (args[1])

    def on_active_file_changed (self, *args):
        self.titlebar.set_title (args[1])

    def on_sidebar_size_change (self, widget, allocation):
        self.titlebar.set_left_header_width (allocation.width)

    def on_close (self, *args):
        # We don't want to close while some files are still saving
        for file_object in self.file_manager.get_open_files ():
            while threading.activeCount() > 1:
                pass
            else:
                file_object.close ()

        # Write some settings
        # Get the open files

        open_paths = list ()
        for file_obj in self.file_manager.get_open_files ():
            open_paths.append (file_obj.get_path ())

        self.app_settings.set_strv ("opened-files", open_paths)

        Gtk.main_quit ()


window = MarkItWindow ()
Gtk.main ()
