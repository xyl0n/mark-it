#!/usr/bin/env python

from gi.repository import Gtk, GObject

class MarkItTitleBar (Gtk.Box):

    __gsignals__ = {
        'file_create_requested': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'folder_create_requested': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__ (self, file_manager):
        Gtk.Box.__init__ (self)

        self.file_manager = file_manager

        # Make the titlebar
        # This is for document specific actions
        self.right_header = Gtk.HeaderBar ()
        self.right_header.set_title ("Mark It") # TODO: Replace this with the loaded file
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

        self.pack_start (self.document_nav_header, False, False, 0)
        self.pack_start (Gtk.Separator.new (Gtk.Orientation.VERTICAL), False, False, 0)
        self.pack_start (self.right_header, True, True, 0)

    def set_title (self, title):
        self.right_header.set_title (title)

    def set_left_header_width (self, width):
        self.document_nav_header.set_size_request (width, -1)

    def create_new_file (self, *args):
        self.emit ('file_create_requested')

    def create_new_folder (self, *args):
        self.emit ('folder_create_requested')
