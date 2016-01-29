#!/usr/bin/env python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

from filemanager import MarkItFileManager
from textview import MarkItTextView
from documentview import MarkItDocumentView
from workspaceview import MarkItWorkspaceView

class MarkItSidebar (Gtk.Box):

    __gsignals__ = {
        'active_file_changed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }


    def __init__ (self, file_manager, view_stack):
        Gtk.Box.__init__ (self)

        self.file_manager = file_manager
        self.document_view = MarkItDocumentView (self.file_manager)
        self.stack = view_stack
        self.set_orientation (Gtk.Orientation.VERTICAL)
        self.set_size_request (200, -1)
        self.get_style_context().add_class ("markit-sidebar")
        self.get_style_context().add_class ("sidebar")
        self.get_style_context().add_class ("view")
        self.file_manager.connect ("file_added", self.on_file_added)

        if len(self.file_manager.get_file_list()) == 0:
            self.file_manager.create_new_file ()

        self.setup_workspace_view ()
        self.setup_document_view ()

    def setup_workspace_view (self):
        workspace_label = Gtk.Label ("<b>Workspace</b>")
        workspace_label.set_use_markup (True)
        workspace_label.get_style_context().add_class ("dim-label")
        workspace_label.set_alignment (0.0, 0.5)
        workspace_label.set_margin_left (12)

        self.pack_start (workspace_label, False, False, 6)

        self.workspace_view = MarkItWorkspaceView (self.file_manager)
        self.pack_start (self.workspace_view, False, False, 0)

        self.workspace_view.connect ('file_clicked', self.on_workspace_file_clicked)

    def setup_document_view (self):
        doc_label = Gtk.Label ("<b>Documents</b>")
        doc_label.set_use_markup (True)
        doc_label.get_style_context().add_class ("dim-label")
        doc_label.set_alignment (0.0, 0.5)
        doc_label.set_margin_left (12)

        self.pack_start (doc_label, False, False, 6)

        self.pack_end (self.document_view, True, True, 0)

    def on_file_added (self, *args):
        # Insert a new entry on document browser
        file_obj = self.file_manager.get_file_object_from_name (args[1])
        self.document_view.add_row (file_obj)
        # TODO: Add new page to stack

    def on_workspace_file_clicked (self, *args):
        self.stack.set_visible_child_name (args[1])
        self.emit ('active_file_changed', args[1])

'''
class MarkItSidebar (Gtk.Box):
    # A class which handles the sidebar used to switch and present files

    def __init__ (self, files):

        self.file_stack = Gtk.Stack ()

        self.setup_file_browser ()

        if len(self.file_manager.get_file_list()) == 0:
            self.file_manager.create_new_file ()

        doc_label = Gtk.Label ("<b>Documents</b>")
        doc_label.set_use_markup (True)
        doc_label.get_style_context().add_class ("dim-label")
        doc_label.set_alignment (0.0, 0.5)
        doc_label.set_margin_left (12)

        self.pack_start (Gtk.Separator.new (Gtk.Orientation.HORIZONTAL), False, False, 12)

        self.pack_start (doc_label, False, False, 6)
        self.pack_end (MarkItDocumentView(), True, True, 0)

    def get_stack (self):
        return self.file_stack

    def setup_file_browser (self):
        workspace_label = Gtk.Label ("<b>Workspace</b>")
        workspace_label.set_use_markup (True)
        workspace_label.get_style_context().add_class ("dim-label")
        workspace_label.set_alignment (0.0, 0.5)
        workspace_label.set_margin_left (12)

        self.pack_start (workspace_label, False, False, 6)

        self.file_listbox = MarkItWorkspaceView ()
        self.pack_start (self.file_listbox, False, False, 0)


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
'''
