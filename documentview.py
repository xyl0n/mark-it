#!/usr/bin/evn python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

from filemanager import MarkItFileManager

class MarkItDocumentView (Gtk.ListBox):

    # This is a custom class essentially because idk Gtk Treeview sucks

    __gsignals__ = {
        'row_clicked': (GObject.SIGNAL_RUN_FIRST, None, (str, bool, str)), # Name, if it's a folder, and name of parent folder
    }

    def __init__ (self, file_manager):
        Gtk.ListBox.__init__ (self)
        self.file_manager = file_manager

        self.connect ('row_activated', self.on_row_clicked)

        for file_obj in file_manager.get_file_list ():
            if file_obj.get_is_folder () == False:
                if file_obj.get_parent_folder () == None:
                    file_label = self.create_row (file_obj.get_name())
                    row = Gtk.ListBoxRow ()
                    row.add (file_label)
                    self.insert (row, -1)

    def create_row (self, label):
        file_label = Gtk.Label (label)
        file_label.set_alignment (0.0, 0.5)
        file_label.set_margin_left (16)
        file_label.get_style_context ().add_class ('markit-sidebar-row')
        return file_label

    def add_row (self, file_obj):
        if file_obj.get_is_folder () == False:
            if file_obj.get_parent_folder () == None:
                file_label = self.create_row (file_obj.get_name ())
                row = Gtk.ListBoxRow ()
                row.add (file_label)
                index = self.file_manager.get_index_of_file (file_obj.get_name ())
                print (index)
                self.insert (row, index)

        self.show_all ()

    def on_row_clicked (self, *args):
        pass


'''
class MarkItDocumentView (Gtk.TreeView):

    def __init__ (self, file_manager):
        Gtk.TreeView.__init__ (self)
        # General settings
        self.set_headers_visible (False)
        self.get_selection ().set_mode (Gtk.SelectionMode.SINGLE)
        self.connect ("row_activated", self.on_row_clicked)

        # Make columns - Just one for now for the file name
        name_renderer = Gtk.CellRendererText()
        name_column = Gtk.TreeViewColumn ("File", name_renderer, text = 0)
        self.append_column (name_column)

        self.tree_store = Gtk.TreeStore (str)

        self.set_model (self.tree_store)

        for file_obj in file_manager.get_file_list ():
            if file_obj.get_is_folder () == False:
                if file_obj.get_parent_folder () == None:
                    file_iter = self.tree_store.append (None, [file_obj.get_name ()])

        self.show_all ()

    def add_row (self, file_obj):
        if file_obj.get_is_folder () == False:
            if file_obj.get_parent_folder () == None:
                self.tree_store.append (None, [file_obj.get_name ()])

    def on_row_clicked (self, tree, path, column):

        (model, pathlist) = self.get_selection ().get_selected_rows()

        for path in pathlist :
            tree_iter = tree.get_model ().get_iter (path)
            value = model.get_value(tree_iter,0)
            print (value)

        self.get_selection ().unselect_all ()
'''
