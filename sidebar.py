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

        self.setup_workspace_view ()
        self.setup_document_view ()

        self.file_manager.connect ("file_created", self.on_file_creation)
        self.file_manager.connect ("file_opened", self.on_file_open)

        if len(self.file_manager.get_file_list()) == 0:
            self.file_manager.create_new_file () # TODO: if opened files are also zero

        self.document_view.connect ("cursor_changed", lambda *args: self.workspace_view.unselect_all ())

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
        self.workspace_view.connect ('file_close_requested', self.on_workspace_file_closed)

    def setup_document_view (self):
        doc_label = Gtk.Label ("<b>Documents</b>")
        doc_label.set_use_markup (True)
        doc_label.get_style_context().add_class ("dim-label")
        doc_label.set_alignment (0.0, 0.5)
        doc_label.set_margin_left (12)

        self.pack_start (doc_label, False, False, 6)

        self.pack_end (self.document_view, True, True, 0)

        self.document_view.connect ("file_clicked", self.on_document_file_clicked)

    def on_file_creation (self, *args):
        # Insert a new entry on document browser
        file_obj = self.file_manager.get_file_object_from_name (args[1])
        self.document_view.add_row (file_obj)

    def on_file_open (self, *args):
        # Insert a new row on the workspace view
        file_obj = self.file_manager.get_file_object_from_path (args[1])
        self.workspace_view.add_row (file_obj)

    def on_workspace_file_clicked (self, *args):
        self.stack.set_page (args[1])
        name = self.file_manager.path_to_name (args[1])
        self.emit ('active_file_changed', name)
        self.document_view.get_selection ().unselect_all ()

    def on_document_file_clicked (self, *args):
        self.file_manager.open_file (args[1])

    def on_workspace_file_closed (self, *args):
        # But first we need to close the gtk stack
        self.stack.close_page (args[1])

        self.file_manager.close_file (args[1])

    def hide_widgets (self):
        for widget in self.workspace_view.hidden_widgets:
            widget.hide ()

        if self.workspace_view.initial_visible_widget != None:
            self.workspace_view.initial_visible_widget.show ()
