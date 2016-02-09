#!/usr/bin/evn python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

from filemanager import MarkItFileManager

import copy

class MarkItDocumentView (Gtk.TreeView):

    TARGETS = [
        (Gtk.TargetEntry.new ("File Row", Gtk.TargetFlags.SAME_WIDGET, 0)),
        (Gtk.TargetEntry.new ("Folder Row", Gtk.TargetFlags.SAME_WIDGET, 1))
    ]

    __gsignals__ = {
        'file_clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }

    def __init__ (self, file_manager):
        Gtk.TreeView.__init__ (self)
        # General settings
        self.set_headers_visible (False)
        self.get_selection ().set_mode (Gtk.SelectionMode.SINGLE)
        self.connect ("row_activated", self.on_row_clicked)
        self.file_manager = file_manager

        self.get_style_context().add_class ("sidebar")
        self.get_style_context().add_class ("view")

        self.enable_model_drag_source (Gdk.ModifierType.BUTTON1_MASK,
                                       self.TARGETS, Gdk.DragAction.MOVE)
        self.enable_model_drag_dest (self.TARGETS,
                                     Gdk.DragAction.MOVE)
        self.connect("drag_data_get", self.on_drag_data_get)
        self.connect("drag_data_received", self.on_drag_data_receive)

        # Make columns - Just one for now for the file name
        name_renderer = Gtk.CellRendererText()
        name_column = Gtk.TreeViewColumn ("File", name_renderer, text = 0)
        self.append_column (name_column)

        self.tree_store = Gtk.TreeStore (str)

        self.set_model (self.tree_store)

        self.folder_iters = {} # A dictionary to store the iter for each folder
        temp_folder_list = list(self.file_manager.get_folder_list ())

        self.add_folders (temp_folder_list, 0)

        for file_obj in self.file_manager.get_file_list ():
            if file_obj.get_is_folder () == False:
                if file_obj.get_parent_folder () == None:
                    file_iter = self.tree_store.append (None, [file_obj.get_name ()])
                else:
                    last_index = file_obj.get_parent_folder ().rfind("/")
                    #print (last_index)
                    if last_index == -1:
                        parent_string = file_obj.get_parent_folder ()
                    else:
                        parent_string = file_obj.get_parent_folder ()[last_index + 1:]

                    parent_folder_iter = self.folder_iters[parent_string]
                    file_iter = self.tree_store.append (parent_folder_iter, [file_obj.get_name ()])

        self.get_selection ().connect ("changed", self.on_selection_change)
        self.show_all ()

    def add_folders (self, folder_list, call_number):
        orphan_folders = list ()

        for folder_obj in folder_list:
            # This adds the top level folders
            if folder_obj.get_parent_folder () == None:
                folder_iter = self.tree_store.append (None, [folder_obj.get_name ()])
                self.folder_iters[folder_obj.get_name ()] = folder_iter
            else:
                # These folders have a parent folder
                last_index = folder_obj.get_parent_folder ().rfind("/") # We only want the parent directory, not the whole path
                                                                        # This should ideally be done when creating the object
                if last_index == -1:
                    parent_string = folder_obj.get_parent_folder ()
                else:
                    parent_string = folder_obj.get_parent_folder ()[last_index + 1:]

                if self.folder_iters.get (parent_string) != None:
                    # These folders' parents are already in the tree, so we can add them
                    parent_iter = self.folder_iters [parent_string]
                    folder_iter = self.tree_store.append (parent_iter, [folder_obj.get_name ()])
                    self.folder_iters[folder_obj.get_name ()] = folder_iter
                else:
                    orphan_folders.append (folder_obj)

        # All the folders with parents in the tree have been added
        if len (folder_list) != 0:
            call_number += 1
            # If we have folders still not in the tree
            self.add_folders (orphan_folders, call_number)


    def add_row (self, file_obj):
        if file_obj.get_parent_folder () == None:
            self.tree_store.append (None, [file_obj.get_name ()])

    def get_path_for_folder (self, folder_obj):
        pass

    def on_selection_change (self, selection):
        store, paths = selection.get_selected_rows ()
        # Idk


    def on_drag_data_get (self, treeview, context, selection_data, target_id, time):
        pass

    def on_drag_data_receive (self, treeview, context, x, y, selection_data, target_id, time):
        pass

    def on_row_clicked (self, tree, path, column):

        (model, pathlist) = self.get_selection ().get_selected_rows()

        for path in pathlist:
            directory_list = list ()

            node_end = False

            while node_end == False:
                tree_iter = tree.get_model ().get_iter (path)
                value = model.get_value(tree_iter, 0)
                directory_list.append (value)
                if path.get_depth () > 1:
                    path.up ()
                else:
                    node_end = True


        full_path = self.file_manager.get_app_dir ()
        for name in list(reversed(directory_list)):
            full_path += name + "/"

        self.emit ("file_clicked", full_path)
