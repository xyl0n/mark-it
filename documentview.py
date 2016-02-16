#!/usr/bin/evn python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

import filemanager

import copy


class MarkItDocumentView (Gtk.TreeView):

    __gsignals__ = {
        'file_clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'file_move_requested': (GObject.SIGNAL_RUN_FIRST, None, (str, str, int)),
    }

    class MarkItTreeStore (Gtk.TreeStore):

        __gsignals__ = {
            # We want to emit this if a row is dropped into a new folder
            # 1st arg is source path, 2nd is dest arg, 3rd is file type
            'row_hierarchy_changed' : (GObject.SIGNAL_RUN_FIRST, None, (str, str, int)),
        }

        def __init__ (self, *column_types, tree_view):
            Gtk.TreeStore.__init__ (self)
            self.set_column_types (column_types)

            self.parent_tree = tree_view

            self.file_source_path = None
            self.file_type = None
            self.file_dest_path = None

        def do_drag_data_delete (self, path):

            try:
                tree_iter = self.get_iter (path)
                self.remove (tree_iter)

                # I think the drag_data_delete should be called after it is
                # checked if the row_drop is possible so these variables should have values
                self.emit ("row_hierarchy_changed", self.file_source_path, self.file_dest_path, self.file_type)

                return True
            except ValueError:
                return False

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

            if src_path.get_depth () == dest_path.get_depth ():
                return False # We only want to drop into a different folder

            if dest_path.get_depth () > 1:
                tmp_path = dest_path.copy ()
                tmp_path.up ()

                # This bit is new B)
                parent_obj = self.parent_tree.convert_tree_path_to_file_object (tmp_path)
                if parent_obj.get_is_folder () == False: # So if it is a file
                    return False

                # If the parent doesn't exist
                # Idk what's happening here I'm just copying the original source code
                try:
                    self.parent_tree.get_model ().get_iter (tmp_path)
                except ValueError:
                    return False

            file_obj = self.parent_tree.convert_tree_path_to_file_object (src_path)
            self.file_source_path = file_obj.get_path ()
            if file_obj.get_is_folder () == False:
                self.file_type = self.parent_tree.file_manager.FileTypes.FILE.value
            else:
                self.file_type = self.parent_tree.file_manager.FileTypes.FOLDER.value

            last_index = self.file_source_path.rfind ("/")
            file_name = file_obj.get_name ()

            self.file_dest_path = self.parent_tree.create_file_path_from_tree_path (dest_path, file_name)

            return True

    def __init__ (self, file_manager):
        Gtk.TreeView.__init__ (self)
        # General settings
        self.set_headers_visible (False)
        self.get_selection ().set_mode (Gtk.SelectionMode.SINGLE)
        self.connect ("row_activated", self.on_row_clicked)
        self.file_manager = file_manager
        self.file_manager.connect ("file_renamed", self.on_file_rename)

        self.file_type_icons = dict ()
        self.file_type_icons[self.file_manager.FileTypes.FILE] = "folder-documents-symbolic"
        self.file_type_icons[self.file_manager.FileTypes.FOLDER] = "folder-symbolic"

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
        self.tree_store.connect ("row_hierarchy_changed", self.on_row_move)

        self.set_model (self.tree_store)

        self.folder_iters = {} # A dictionary to store the iter for each folder
        temp_folder_list = list(self.file_manager.get_folder_list ())

        self.add_folders (temp_folder_list, 0)

        for file_obj in self.file_manager.get_file_list ():
            if file_obj.get_is_folder () == False:
                if file_obj.get_parent_folder () == None:
                    file_iter = self.tree_store.append (None, [file_obj.get_name (), self.file_type_icons.get(self.file_manager.FileTypes.FILE)])
                else:
                    last_index = file_obj.get_parent_folder ().rfind("/")
                    if last_index == -1:
                        parent_string = file_obj.get_parent_folder ()
                    else:
                        parent_string = file_obj.get_parent_folder ()[last_index + 1:]

                    parent_folder_iter = self.folder_iters[parent_string]
                    file_iter = self.tree_store.append (parent_folder_iter, [file_obj.get_name (), self.file_type_icons.get(self.file_manager.FileTypes.FILE)])

        self.get_selection ().connect ("changed", self.on_selection_change)
        self.show_all ()


    def add_folders (self, folder_list, call_number):
        orphan_folders = list ()

        for folder_obj in folder_list:
            # This adds the top level folders
            if folder_obj.get_parent_folder () == None:
                folder_iter = self.tree_store.append (None, [folder_obj.get_name (), self.file_type_icons.get(self.file_manager.FileTypes.FOLDER)])
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
                    folder_iter = self.tree_store.append (parent_iter, [folder_obj.get_name (), self.file_type_icons.get(self.file_manager.FileTypes.FOLDER)])
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
                icon = self.file_type_icons[self.file_manager.FileTypes.FOLDER]
            else:
                icon = self.file_type_icons[self.file_manager.FileTypes.FILE]

            self.tree_store.append (None, [file_obj.get_name (), icon])

    def get_path_for_folder (self, folder_obj):
        pass

    def on_selection_change (self, selection):
        pass

    def on_file_rename (self, *args):
        old_path = args[1]
        old_name = args[2]
        new_name = args[3]

        self.get_model ().foreach (self.row_iterate_func, args)

    def row_iterate_func (self, model, path, iter, args):
        old_path = args[1]
        old_name = args[2]
        new_name = args[3]

        name = model.get_value (iter, 0)
        file_type = model.get_value (iter, 1)

        file_path = self.create_file_path_from_tree_path (path, name)
        if file_path == old_path:
            if file_type == self.file_type_icons[self.file_manager.FileTypes.FILE]:
                model.set_value (iter, 0, new_name)
                return True

        return False


    def on_row_clicked (self, tree, path, column):

        model, paths = self.get_selection ().get_selected_rows()
        file_obj = self.convert_tree_path_to_file_object (paths[0])

        if file_obj.get_is_folder () == False: # We only want to open up files
            self.emit ("file_clicked", file_obj.get_path ())

    # What? Why do I need to add a wrapper around the tree store signal
    # that does the same thing?
    def on_row_move (self, *args):
        self.emit ("file_move_requested", args[1], args[2], args[3])

    # TODO: Clean up the following functions, they're a mess right now

    # We use this to convert the tree path to a physical location on disk
    def convert_tree_path_to_file_object (self, tree_path):
        directory_list = list ()

        node_end = False

        file_icon = None

        while node_end == False:
            tree_iter = self.get_model ().get_iter (tree_path)
            value = self.get_model ().get_value(tree_iter, 0)

            if file_icon == None:
                file_icon = self.get_model ().get_value(tree_iter, 1)

            directory_list.append (value)
            if tree_path.get_depth () > 1:
                tree_path.up ()
            else:
                node_end = True

        full_path = self.file_manager.get_app_dir ()
        for name in list(reversed(directory_list)):
            full_path += name + "/"

        tree_iter = self.get_model ().get_iter (tree_path)

        for key in self.file_type_icons:
            icon = self.file_type_icons.get (key)
            if icon == file_icon:
                file_type = key

        full_path = full_path[:-1]

        if file_type == self.file_manager.FileTypes.FILE:
            file_obj = self.file_manager.get_file_object_from_path (full_path, is_folder = False)
        elif file_type == self.file_manager.FileTypes.FOLDER:
            file_obj = self.file_manager.get_file_object_from_path (full_path, is_folder = True)
        else:
            file_obj = None

        return file_obj

    def create_file_path_from_tree_path (self, tree_path, file_name):
        # We use this when we don't have a file existing a the desired location
        path_str = tree_path.to_string ()
        last_index_of_colon = path_str.rfind(":")

        full_path = None

        if last_index_of_colon != -1:
            path_str = path_str[:last_index_of_colon]

            path = Gtk.TreePath.new_from_string (path_str)
            file_obj = self.convert_tree_path_to_file_object (path)
            full_path = file_obj.get_path () + "/" + file_name
        else:
            full_path = self.file_manager.get_app_dir () + file_name

        return full_path
