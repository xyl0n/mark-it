#!/usr/bin/env python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

from textview import MarkItTextView
from filemanager import MarkItFileManager

class MarkItStack (Gtk.Notebook):

    def __init__ (self, files):
        Gtk.Notebook.__init__ (self)

        self.set_show_tabs (False)
        self.set_show_border (False)

        self.text_view_list = list ()
        self.total_pages = 0

        self.file_manager = files
        self.file_manager.connect ('file_opened', self.on_file_open)

        self.populate ()

        self.show_all ()

    def populate (self):
        for file_obj in self.file_manager.get_open_files ():
            self.add_page (file_obj.get_path ())

    def add_page (self, path):
        text_view = MarkItTextView (self.file_manager.get_file_object_from_path (path))
        self.text_view_list.append (text_view)
        text_scrolled = Gtk.ScrolledWindow ()
        text_scrolled.add (text_view)

        label = Gtk.Label (path)
        self.append_page (text_scrolled, label)
        self.total_pages += 1
        num = self.get_page_number_for_path (path)
        self.set_page (num)

        self.show_all ()

    def set_page (self, path):
        tab_num = self.get_page_number_for_path (path)
        if tab_num != None:
            page = self.get_nth_page (tab_num)
            self.set_current_page (tab_num)

    def on_file_open (self, *args):
        self.add_page (args[1])

    def get_page_number_for_path (self, path):
        for tab_num in range (0, self.get_n_pages()):
            page = self.get_nth_page (tab_num)
            if page.get_children ()[0].get_file_path () == path:
                return tab_num

        return None

    def close_page (self, file_path, next_file_path):
        num = self.get_page_number_for_path (file_path)
        self.get_nth_page (num).get_children ()[0].close_file ()
        self.remove_page (num)
        next_num = self.get_page_number_for_path (next_file_path)
        if next_num != None:
            self.set_page (next_file_path)
