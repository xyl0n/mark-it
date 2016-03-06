#!/usr/bin/env python

from gi.repository import Gtk, GObject

class MarkItDialogManager (GObject.GObject):

    __gsignals__ = {
        'name_dialog_response': (GObject.SIGNAL_RUN_FIRST, None, (str, int, GObject.TYPE_PYOBJECT,)),
        'name_dialog_canceled': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
    }

    def __init__ (self, window):
        GObject.GObject.__init__ (self)
        self.window = window
        self.dialog_ids = dict ()
        self.dialog_data = dict ()


    def on_name_dialog_response (self, dialog, id):
        dialog_id = None
        for key, val in self.dialog_ids.items():
            if val == dialog:
                dialog_id = key

        if id == 1:
            text = dialog.get_content_area ().get_children ()[0].get_text ()
            self.emit ('name_dialog_response', text, dialog_id, self.dialog_data.get(dialog))
        elif id == 0:
            self.destroy_dialog (dialog_id)

    # This creates a dialog asking for a name, used when
    # renaming files, making new folders etc.
    # user_data is a tuple
    def create_name_dialog (self, title, action_string, default_string, dialog_id, *user_data):
        dialog = Gtk.Dialog ()
        dialog_content = dialog.get_content_area ()

        entry = Gtk.Entry ()
        entry.set_text (default_string)

        entry.set_margin_left (12)
        entry.set_margin_right (12)
        entry.set_margin_top (12)
        entry.set_margin_bottom (12)

        dialog_content.add (entry)

        dialog.add_button ("Cancel", 0)
        dialog.add_button (action_string, 1)

        dialog.set_modal (True)
        dialog.set_transient_for (self.window)

        dialog.set_title (title)

        self.dialog_ids [dialog_id] = dialog
        self.dialog_data [dialog] = user_data

        dialog.show_all ()
        dialog.connect ("response", self.on_name_dialog_response)
        dialog.run ()

    def destroy_dialog (self, dialog_id):
        dialog = self.dialog_ids.get (dialog_id)
        self.dialog_data.pop (dialog, None)
        self.dialog_ids.pop (dialog_id, None)
        dialog.destroy ()
