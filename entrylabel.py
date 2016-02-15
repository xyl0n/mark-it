#!/usr/bin/env python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

class MarkItEntryLabel (Gtk.Box):

    def __init__ (self, text):
        Gtk.Box.__init__ (self)

        self.label = Gtk.Label (text)
        self.entry = Gtk.Entry ()
        self.entry.set_text (text)
        self.entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, "go-next-symbolic")

        self.pack_start (self.label, True, True, 0)
        self.pack_start (self.entry, True, True, 0)

    def hide (self):
        self.entry.hide ()
        self.label.show ()

    def show_entry (self):
        self.entry.show ()
        self.label.hide ()

    def get_label (self):
        return self.label

    def get_entry (self):
        return self.entry

    def set_text (self, text):
        self.label.set_text (text)
        self.entry.set_text (text)
