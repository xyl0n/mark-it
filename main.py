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

        self.load_settings ()

        self.file_manager = MarkItFileManager (self.opened_files)

        style = Gtk.CssProvider ()
        style.load_from_path ("style.css")
        self.get_style_context ().add_provider_for_screen (Gdk.Screen.get_default (),
                                                           style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.create_interface ()

        self.show_all ()

        self.sidebar.hide_widgets ()

    def load_settings (self):
        self.app_settings = Gio.Settings.new ("org.gnome.mark-it.saved-state")
        self.opened_files = list ()

        for file_path in self.app_settings.get_strv("opened-files"):
            if file_path != '':
                self.opened_files.append (file_path)

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
        self.right_header.set_title ("Untitled 1") # TODO: Replace this with the loaded file
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

        # This is for buttons related to file editing

        undo_button = Gtk.Button ().new_from_icon_name ("edit-undo-symbolic", 1)
        redo_button = Gtk.Button ().new_from_icon_name ("edit-redo-symbolic", 1)
        self.right_header.pack_start (undo_button)
        self.right_header.pack_start (redo_button)

        search_button = Gtk.Button ().new_from_icon_name ("edit-find-symbolic", 1)
        self.right_header.pack_start (search_button)

        export_button = Gtk.Button ().new_from_icon_name ("document-export-symbolic", 1)
        self.right_header.pack_start (export_button)

        # End

        preferences_button = Gtk.Button ().new_from_icon_name ("view-more-symbolic", 1)
        self.right_header.pack_end (preferences_button)

        self.right_header.pack_end (Gtk.Separator.new (Gtk.Orientation.VERTICAL))

        delete_button = Gtk.Button ().new_from_icon_name ("user-trash-symbolic", 1)
        self.right_header.pack_end (delete_button)

        timeline_button = Gtk.Button ().new_from_icon_name ("document-open-recent-symbolic", 1)
        self.right_header.pack_end (timeline_button)

        upload_button = Gtk.Button ().new_from_icon_name ("send-to-symbolic", 1)
        self.right_header.pack_end (upload_button)

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
        # Lets make a dialog to get the name of the folder
        name_dialog = Gtk.Dialog ()
        dialog_content = name_dialog.get_content_area ()

        name_entry = Gtk.Entry ()
        default_name = "Untitled Folder " + str(self.file_manager.folder_count + 1)
        name_entry.set_text (default_name)
        name_entry.set_margin_left (12)
        name_entry.set_margin_right (12)
        name_entry.set_margin_top (12)
        name_entry.set_margin_bottom (12)
        dialog_content.add (name_entry)

        name_dialog.add_button ("Cancel", 0)
        name_dialog.add_button ("Create", 1)

        name_dialog.set_modal (True)
        name_dialog.set_transient_for (self)

        name_dialog.set_title ("Create New Folder")

        name_dialog.show_all ()
        name_dialog.connect ("response", self.on_folder_dialog_response)
        name_dialog.run ()

    def on_folder_dialog_response (self, dialog, id):
        if id == 1:
            name = dialog.get_content_area ().get_children ()[0].get_text ()
            self.file_manager.create_new_folder (name)

        dialog.destroy ()

    def on_active_file_changed (self, *args):
        self.right_header.set_title (args[1])

    def on_sidebar_size_change (self, widget, allocation):
        self.document_nav_header.set_size_request (allocation.width, -1)

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
