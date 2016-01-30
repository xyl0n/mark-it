#!/usr/bin/evn python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

from filemanager import MarkItFileManager

class MarkItDocumentView (Gtk.TreeView):

    def __init__ (self, file_manager):
        Gtk.TreeView.__init__ (self)
        # General settings
        self.set_headers_visible (False)
        self.get_selection ().set_mode (Gtk.SelectionMode.SINGLE)
        self.connect ("row_activated", self.on_row_clicked)

        self.get_style_context ().add_class ("list")

        # Make columns - Just one for now for the file name
        name_renderer = Gtk.CellRendererText()
        name_column = Gtk.TreeViewColumn ("File", name_renderer, text = 0)
        self.append_column (name_column)

        self.tree_store = Gtk.TreeStore (str)

        self.set_model (self.tree_store)

        self.folder_iters = {}

        for folder_obj in file_manager.get_folder_list ():
            folder_iter = self.tree_store.append (None, [folder_obj.get_name ()])
            self.folder_iters[folder_obj.get_name ()] = folder_iter

        for file_obj in file_manager.get_file_list ():
            if file_obj.get_is_folder () == False:
                if file_obj.get_parent_folder () == None:
                    file_iter = self.tree_store.append (None, [file_obj.get_name ()])
                else:
                    parent_folder_iter = self.folder_iters[file_obj.get_parent_folder ()]
                    file_iter = self.tree_store.append (parent_folder_iter, [file_obj.get_name ()])

        self.show_all ()

    def add_row (self, file_obj):
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
class MarkItDocumentView (Gtk.ListBox):

    # This is a custom class essentially because idk Gtk Treeview sucks
    # I changed my mind

    __gsignals__ = {
        'row_clicked': (GObject.SIGNAL_RUN_FIRST, None, (str, bool, str)), # Name, if it's a folder, and name of parent folder
    }

    def __init__ (self, file_manager, icon_theme):
        Gtk.ListBox.__init__ (self)
        self.file_manager = file_manager
        self.icon_theme = icon_theme

        self.connect ('row_activated', self.on_row_clicked)

        self.left_padding = 0

        for folder_obj in file_manager.get_folder_list ():
            # Create a folder thing
            if folder_obj.get_parent_folder () == None:
                # We can make a row
                folder_row = self.create_folder_row (folder_obj.get_name ())
                row = Gtk.ListBoxRow ()
                row.add (folder_row)
                self.insert (row, -1)

        for file_obj in file_manager.get_file_list ():
            self.add_row (file_obj)

    def create_row (self, label):
        file_label = Gtk.Label (label)
        file_label.set_alignment (0.0, 0.5)
        file_label.set_margin_left (self.left_padding)
        file_label.get_style_context ().add_class ('markit-sidebar-row')
        layout = Gtk.Box.new (Gtk.Orientation.HORIZONTAL, 0)
        layout.pack_start (file_label, True, True, 0)

        return layout

    def create_folder_row (self, label):
        layout = Gtk.Box.new (Gtk.Orientation.HORIZONTAL, 0)

        expander_pix = self.icon_theme.load_icon ("document-view-expander-closed-symbolic", 8, Gtk.IconLookupFlags.FORCE_SYMBOLIC)
        expander_icon = Gtk.Image.new_from_pixbuf (expander_pix)
        #expander_button.set_image (expander_icon)

        expander_button = Gtk.Button.new_from_icon_name ("document-view-expander-closed-symbolic", 12)
        img = expander_button.get_image ()
        img.set_pixel_size (8)

        expander_button.get_style_context ().add_class ("markit-document-expander")
        expander_button.get_style_context ().add_class ("flat")

        layout.pack_start (expander_button, False, False, 0)
        folder_label = Gtk.Label (label)
        folder_label.set_alignment (0.0, 0.5)
        folder_label.set_margin_left (8)
        layout.pack_start (folder_label, True, True, 0)

        layout.connect ("size_allocate", self.on_expander_size_allocate)

        return layout

    def on_expander_size_allocate (self, widget, allocation):
        # Make everything line up
        self.left_padding = allocation.width - widget.get_children ()[1].get_allocation ().width

        for row in self.get_children ():
            for widget in row.get_children ():
                if isinstance (widget.get_children()[0], Gtk.Label): # Yeah referencing widgets like this is bad for maintenance
                    if widget.get_children()[0].get_margin_left () != self.left_padding + 6:
                        widget.get_children()[0].set_margin_left (self.left_padding)

    def add_row (self, file_obj):
        if file_obj.get_is_folder () == False:
            if file_obj.get_parent_folder () == None:
                file_label = self.create_row (file_obj.get_name ())
                row = Gtk.ListBoxRow ()
                row.add (file_label)
                index = self.file_manager.get_index_of_file (file_obj.get_name ())
                print (index)
                self.insert (row, index)
            else:
                # The file has a parent folder
                file_label = self.create_row (file_obj.get_name ())
                row = Gtk.ListBoxRow ()
                row.add (file_label)
                row.set_margin_left (6)

                index = -1

                for rows in self.get_children ():
                    i = 0
                    i += 1
                    for widget in rows.get_children ():
                        if isinstance (widget.get_children()[0], Gtk.Label):
                            if widget.get_children()[0].get_text () == file_obj.get_parent_folder ():
                                index = i

                self.insert (row, index)

        self.show_all ()

    def on_row_clicked (self, *args):
        pass
'''
