#!/usr/bin/env python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango

from textview import MarkItTextView

class MarkItWindow(Gtk.Window):

    def __init__ (self):
        Gtk.Window.__init__(self)
        self.set_title ("Mark It")
        self.set_default_size (1200, 800)

        self.create_textview ()

    def create_textview (self):
        self.box = Gtk.Box ()

        self.text_view = MarkItTextView ()
        self.text_scrolled = Gtk.ScrolledWindow ()
        self.text_scrolled.add (self.text_view)
        self.box.pack_start (self.text_scrolled, True, True, 0)

        self.add (self.box)


window = MarkItWindow ()
window.connect('delete-event', Gtk.main_quit)
window.show_all ()
Gtk.main ()
