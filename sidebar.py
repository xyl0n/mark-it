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

    def __init__ (self, file_manager, view_stack, dialog_manager):
        Gtk.Box.__init__ (self)

        self.file_manager = file_manager
        self.document_view = MarkItDocumentView (self.file_manager)
        self.stack = view_stack
        self.dialog_manager = dialog_manager
        self.set_orientation (Gtk.Orientation.VERTICAL)
        self.set_size_request (200, -1)
        self.get_style_context().add_class ("markit-sidebar")

        self.setup_workspace_view ()
        self.setup_document_view ()

        self.file_manager.connect ("file_created", self.on_file_creation)
        self.file_manager.connect ("file_opened", self.on_file_open)
        self.file_manager.connect ("folder_created", self.on_folder_creation)

        self.dialog_manager.connect ("name_dialog_response", self.on_name_dialog_response)

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
        self.workspace_view.connect ('file_rename_requested', self.on_workspace_file_rename_request)

    def setup_document_view (self):
        doc_label = Gtk.Label ("<b>Documents</b>")
        doc_label.set_use_markup (True)
        doc_label.get_style_context().add_class ("dim-label")
        doc_label.set_alignment (0.0, 0.5)
        doc_label.set_margin_left (12)

        self.pack_start (doc_label, False, False, 6)

        doc_scrolled = Gtk.ScrolledWindow ()
        doc_scrolled.add (self.document_view)
        self.pack_end (doc_scrolled, True, True, 0)

        self.document_view.connect ("file_clicked", self.on_document_file_clicked)
        self.document_view.connect ("file_move_requested", self.on_document_move_request)

    def on_file_creation (self, *args):
        # Insert a new entry on document browser
        file_obj = self.file_manager.get_file_object_from_path (args[1])
        self.document_view.add_row (file_obj)

    def on_folder_creation (self, *args):

        folder_obj = self.file_manager.get_file_object_from_path (args[1], is_folder = True)
        self.document_view.add_row (folder_obj)

    def on_file_open (self, *args):
        # Insert a new row on the workspace view
        # I think checking if the file is already open is taken care of somewhere
        # else so we're fine to do this
        file_obj = self.file_manager.get_file_object_from_path (args[1])
        self.workspace_view.add_row (file_obj)

    def on_workspace_file_clicked (self, *args):
        self.stack.set_page (args[1])
        name = self.file_manager.path_to_name (args[1])
        self.emit ('active_file_changed', name)
        self.document_view.get_selection ().unselect_all ()

    def on_workspace_file_rename_request (self, *args):
        name = self.file_manager.path_to_name (args[1])
        path = args[1]
        self.dialog_manager.create_name_dialog ("Rename file", "Rename", name, 2, (path))

    def on_name_dialog_response (self, *args):
        text = args[1]
        id = args[2]
        path = args[3]
        print ("\n\n\n")
        print (args)
        path = path[0]

        self.file_manager.rename_file (path, text)

    def on_document_file_clicked (self, *args):
        file_obj = self.file_manager.get_file_object_from_path (args[1])

        if file_obj.get_is_open () != True:
            self.file_manager.open_file (args[1])

        row = self.workspace_view.get_row_for_path (args[1])
        if row != None:
            self.workspace_view.select_row (row)

    def on_document_move_request (self, *args):
        obj = args[1]
        new_path = args[2]
        if obj == None:
            print ("Couldn't find file or folder at this path")
            # We need to do a dialog box or smth maybe
            return

        if obj.get_is_folder ():
            self.file_manager.move_folder (obj, new_path)
        else:
            self.file_manager.move_file (obj.get_path (), new_path)


    def on_workspace_file_closed (self, *args):
        # But first we need to close the pages
        self.stack.close_page (args[1], args[2])
        self.file_manager.close_file (args[1])

    def hide_widgets (self):
        for widget in self.workspace_view.hidden_widgets:
            widget.hide ()

        if self.workspace_view.initial_visible_widget != None:
            self.workspace_view.initial_visible_widget.show ()
