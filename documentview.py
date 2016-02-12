#!/usr/bin/evn python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

from filemanager import MarkItFileManager

import copy

class MarkItDocumentView (Gtk.TreeView):

    __gsignals__ = {
        'file_clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'file_moved': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }

    class MarkItTreeStore (Gtk.TreeStore):

        def __init__ (self, *column_types, tree_view):
            Gtk.TreeStore.__init__ (self)
            self.set_column_types (column_types)

            self.parent_tree = tree_view

        def do_row_drop_possible (self, dest_path, selection_data):
            # So I'm rewriting the original implementation here but adding
            # some other stuff

            row_data = Gtk.tree_get_row_drag_data (selection_data)
            is_row = row_data [0]
            src_model = row_data [1]
            src_path = row_data [2]

            if is_row == False:
                return False # Obviously

            if src_model != self.parent_tree.get_model ():
                return False # We want to only drop into the same treeview

            if src_path.is_ancestor (dest_path):
                return False # We don't want to drop into the same row

            if dest_path.get_depth () > 1:
                tmp_path = dest_path.copy ()
                tmp_path.up ()

                # This bit is new B)
                parent_obj = self.parent_tree.get_file_from_tree_path (tmp_path, self.parent_tree)
                if parent_obj.get_is_folder () == False: # So if it is a file
                    return False

                # If the parent doesn't exist
                # Idk what's happening I'm just copying the original source code
                try:
                    self.parent_tree.get_model ().get_iter (tmp_path)
                except ValueError:
                    return False

            return True

    def __init__ (self, file_manager):
        Gtk.TreeView.__init__ (self)
        # General settings
        self.set_headers_visible (False)
        self.get_selection ().set_mode (Gtk.SelectionMode.SINGLE)
        self.connect ("row_activated", self.on_row_clicked)
        self.file_manager = file_manager

        self.row_type_file_icon = "folder-documents-symbolic"
        self.row_type_folder_icon = "folder-symbolic"

        self.get_style_context().add_class ("sidebar")
        self.get_style_context().add_class ("view")

        self.set_reorderable (True)

        # Make columns - One for file icon and one for file name

        icon_renderer = Gtk.CellRendererPixbuf()
        icon_column = Gtk.TreeViewColumn("File Icon", icon_renderer, icon_name = 1)
        self.append_column (icon_column)

        name_renderer = Gtk.CellRendererText()
        name_column = Gtk.TreeViewColumn ("File", name_renderer, text = 0)
        self.append_column (name_column)

        self.tree_store = self.MarkItTreeStore (str, str, tree_view = self)

        self.set_model (self.tree_store)

        self.folder_iters = {} # A dictionary to store the iter for each folder
        temp_folder_list = list(self.file_manager.get_folder_list ())

        self.add_folders (temp_folder_list, 0)

        for file_obj in self.file_manager.get_file_list ():
            if file_obj.get_is_folder () == False:
                if file_obj.get_parent_folder () == None:
                    file_iter = self.tree_store.append (None, [file_obj.get_name (), self.row_type_file_icon])
                else:
                    last_index = file_obj.get_parent_folder ().rfind("/")
                    #print (last_index)
                    if last_index == -1:
                        parent_string = file_obj.get_parent_folder ()
                    else:
                        parent_string = file_obj.get_parent_folder ()[last_index + 1:]

                    parent_folder_iter = self.folder_iters[parent_string]
                    file_iter = self.tree_store.append (parent_folder_iter, [file_obj.get_name (), self.row_type_file_icon])

        self.get_selection ().connect ("changed", self.on_selection_change)
        self.show_all ()


    def add_folders (self, folder_list, call_number):
        orphan_folders = list ()

        for folder_obj in folder_list:
            # This adds the top level folders
            if folder_obj.get_parent_folder () == None:
                folder_iter = self.tree_store.append (None, [folder_obj.get_name (), self.row_type_folder_icon])
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
                    folder_iter = self.tree_store.append (parent_iter, [folder_obj.get_name (), self.row_type_folder_icon])
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
            if file_obj.get_is_folder () == True:
                icon = self.row_type_folder_icon
            else:
                icon = self.row_type_file_icon

            self.tree_store.append (None, [file_obj.get_name (), icon])

    def get_path_for_folder (self, folder_obj):
        pass

    def on_selection_change (self, selection):
        store, paths = selection.get_selected_rows ()
        # Idk

    def on_row_clicked (self, tree, path, column):

        (model, pathlist) = self.get_selection ().get_selected_rows()

        file_obj = self.get_file_from_tree_path (pathlist[0], tree)
        if file_obj.get_is_folder () == False: # We only want to open up files
            self.emit ("file_clicked", file_obj.get_path ())

    def get_file_from_tree_path (self, tree_path, tree):

        directory_list = list ()

        node_end = False

        while node_end == False:
            tree_iter = tree.get_model ().get_iter (tree_path)
            value = tree.get_model ().get_value(tree_iter, 0)
            file_type = tree.get_model ().get_value(tree_iter, 1)
            directory_list.append (value)
            if tree_path.get_depth () > 1:
                tree_path.up ()
            else:
                node_end = True

        full_path = self.file_manager.get_app_dir ()
        for name in list(reversed(directory_list)):
            full_path += name + "/"

        full_path = full_path[:-1]

        if file_type == self.row_type_folder_icon:
            file_obj = self.file_manager.get_file_object_from_path (full_path, is_folder = True)
        elif file_type == self.row_type_file_icon:
            file_obj = self.file_manager.get_file_object_from_path (full_path, is_folder = False)
        else:
            file_obj = None

        return file_obj
