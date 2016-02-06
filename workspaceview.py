#!/usr/bin/evn python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

from filemanager import MarkItFileObject

class MarkItWorkspaceView (Gtk.ListBox):

    __gsignals__ = {
        'file_clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,)), # We use paths to identify files
        'file_closed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }

    def __init__ (self, file_manager):
        Gtk.ListBox.__init__ (self)

        self.file_manager = file_manager

        self.path_row_index = dict () # Since we may have multiple rows with the same name but different paths
        self.hidden_widgets = list ()
        self.file_labels = list ()

        self.button_width = 0

        self.mouse_hovering_on_label = False
        self.mouse_hovering_on_button = False

        self.populate ()
        self.connect ('row_activated', self.on_row_clicked)

    def on_row_clicked (self, listbox, row):
        file_path = self.path_row_index [row.get_index ()]
        self.emit ('file_clicked', file_path)

        selected_button = row.get_children ()[0].get_children ()[1]

        for widget in self.hidden_widgets:
            if widget != selected_button:
                widget.hide ()
            else:
                widget.show ()

    def populate (self):

        if len (self.file_manager.get_open_files ()) == 0:
            print ("NO OPEN FILES")
            # We need to actually do something here

        for file_object in self.file_manager.get_open_files ():
            self.add_row (file_object)

        self.show_all ()

    def add_row (self, file_object):
        file_label = Gtk.Label (file_object.get_name ())
        file_label.set_alignment (0.0, 0.5)
        file_label.get_style_context ().add_class ('markit-sidebar-row')
        self.file_labels.append (file_label)

        #row_box = Gtk.Box.new (Gtk.Orientation.HORIZONTAL, 0)
        row_box = Gtk.Grid ()

        close_button = Gtk.Button.new_from_icon_name ("window-close-symbolic", 1)
        close_button.get_style_context ().add_class ("flat")
        close_button.get_style_context ().add_class ("mark-it-document-close")
        self.hidden_widgets.append (close_button)

        close_button.connect ("size_allocate", self.on_button_size_allocate)
        close_button.connect ("show", self.on_button_show)
        close_button.connect ("hide", self.on_button_hide)
        close_button.connect ("clicked", self.on_close_click)

        file_label.set_hexpand (True)

        row_box.attach (close_button, 0, 0, 1, 1)
        row_box.attach (file_label, 1, 0, 1, 1)

        row = Gtk.ListBoxRow ()
        row.add (row_box)
        self.insert (row, -1)
        row_num = row.get_index ()
        self.path_row_index[row_num] = file_object.get_path ()

        self.show_all ()

    def on_close_click (self, button):
        box = button.get_parent ()
        row = box.get_parent ()
        self.emit ("file_closed", self.path_row_index[row.get_index()])

        row.destroy ()

    def on_button_show (self, widget):
        for file_label in self.file_labels:
            file_label.set_margin_left (4)

    def on_button_hide (self, widget):
        for file_label in self.file_labels:
            file_label.set_margin_left (self.button_width + 4)

    def on_button_size_allocate (self, widget, allocation):
        if self.button_width == 0:
            self.button_width = allocation.width
            for file_label in self.file_labels:
                file_label.set_margin_left (self.button_width)
