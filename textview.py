#!/usr/bin/env python

from gi.repository import Gtk, GLib, GObject, GdkPixbuf, Gio, Pango, GtkSource, Gdk

from threading import Thread, Event, Timer
import time

class MarkItTextView (GtkSource.View):

    class ResettingTimer (object):

        # This class has a timer which resets
        # We want to start a timer which executes a function like a normal timer
        # However, if the timer is 'reset', then cancel that timer and create a
        # new timer

        def __init__ (self, interval, function):
            self.interval = interval
            self.function = function

            self.timer = None

        def start (self):
            self.timer = Timer (self.interval, self.function)
            self.timer.start ()

        def restart (self):
            self.timer.cancel ()
            self.start ()

        def join (self):
            self.timer.join ()

    def __init__(self, source_file):
        Gtk.TextView.__init__ (self)

        self.source_file = source_file.get_file_object ()
        self.source_file_path = source_file.get_path ()

        # Set up a threaded timer to auto save the buffer
        self.is_typing = False
        self.auto_save = self.ResettingTimer (0.75, self.save_file)
        self.auto_save.start ()

        # Random settings
        self.set_wrap_mode (Gtk.WrapMode.WORD_CHAR)
        self.set_right_margin (24)
        self.set_top_margin (48)
        self.set_left_margin (48)
        #self.set_highlight_current_line (True)
        self.set_indent_on_tab (True)
        self.set_indent_width (4)
        self.set_insert_spaces_instead_of_tabs (True)
        self.set_tab_width (4)

        self.font_desc = Pango.FontDescription.from_string ("monospace")
        self.override_font (self.font_desc)

        # Various variables
        self.heading_lines = list ()
        self.list_lines = list ()
        self.single_asterisk_tags = list ()
        self.double_asterisk_tags = list ()

        # If we are currently in the process of writing a list
        self.in_list_mode = False

        self.create_tags (self.get_buffer ())

        # We need to adjust the text formatting if it gets changed
        self.get_buffer ().connect("changed", self.on_text_changed)
        self.get_buffer ().connect ("insert-text", self.on_text_insert)

        self.get_buffer().set_text (self.source_file.read())

    def save_file (self):
        self.source_file.seek (0)
        text = self.get_buffer().get_text (self.get_buffer().get_bounds () [0],
                                           self.get_buffer().get_bounds () [1], False)
        self.source_file.write (text)
        self.source_file.truncate ()


    def close_file (self):
        self.auto_save.join ()

    def get_file_path (self):
        return self.source_file_path

    def create_tags (self, buff):
        # Lets make some formatting tags
        self.bold = buff.create_tag (weight = Pango.Weight.BOLD)
        self.italic = buff.create_tag (style = Pango.Style.ITALIC)

        # And for the headings too
        self.heading_tags = list ()
        heading_first_rgba = Gdk.RGBA ()
        # COLOURS
        heading_first_rgba.parse ("#1b7bbf")
        self.heading_first = buff.create_tag (weight = Pango.Weight.BOLD,
                                 foreground_rgba = heading_first_rgba)
                                 #size = 24 * Pango.SCALE)
        self.heading_tags.append (self.heading_first)
        heading_second_rgba = Gdk.RGBA ()
        heading_second_rgba.parse ("#5599c8")
        self.heading_second = buff.create_tag (weight = Pango.Weight.SEMIBOLD,
                                 foreground_rgba = heading_second_rgba)
                                 #size = 18 * Pango.SCALE)
        self.heading_tags.append (self.heading_second)
        heading_third_rgba = Gdk.RGBA ()
        heading_third_rgba.parse ("#659cc3")
        self.heading_third = buff.create_tag (weight = Pango.Weight.SEMIBOLD,
                                 style = Pango.Style.ITALIC,
                                 foreground_rgba = heading_third_rgba)
                                 #size = 16 * Pango.SCALE)
        self.heading_tags.append (self.heading_third)

        # We need to apply appropriate margins to text which needs it
        # We want the heading text to be in line with the document body,
        # so any heading symbols go before it
        self.heading_margins = list ()
        margin = 48
        self.first_margin = buff.create_tag (left_margin = 2 * margin / 3)
        self.heading_margins.append (self.first_margin)
        self.second_margin = buff.create_tag (left_margin = margin / 2)
        self.heading_margins.append (self.second_margin)
        self.third_margin = buff.create_tag (left_margin = margin / 3)
        self.heading_margins.append (self.third_margin)

        self.list_margin = buff.create_tag (left_margin = margin * 1.25)

    def on_text_changed (self, buff):

        self.auto_save.restart ()

        self.check_emphasis (buff, "***")
        self.check_emphasis (buff, "**")
        self.check_emphasis (buff, "__")
        self.check_emphasis (buff, "*")
        self.check_emphasis (buff, "_")
        self.check_headings (buff)
        self.check_lists (buff)

    def on_text_insert (self, buff, location, text, len):
        if text == "\n" and self.in_list_mode == True:
            location_iter = buff.get_iter_at_offset (location.get_offset ())
            buff.insert (location, "- ", -1)
            location.backward_cursor_positions (2)

    def check_headings (self, buff):
        # Okay here's what we gotta do
        # 1. Iterate over every line
        # 2. Check the current line to see what the first [three] characters are
        # 3. Check the number of '#' in them
        # 4. Apply the appropriate tag to the entire line

        # Step 1
        for current_line in range (0, buff.get_line_count()):
            line_iter = buff.get_iter_at_line (current_line)

            # Step 2
            offset = 0
            line_end_iter = buff.get_iter_at_offset(line_iter.get_offset())
            line_end_iter.forward_to_line_end ()

            chars = line_end_iter.get_offset () - line_iter.get_offset ()

            # If the line has more than 3 character, set the offset we want to read to 3
            if (line_end_iter.get_offset () - line_iter.get_offset ()) > 3:
                offset = 3
            # If it has less than that, set it to that amount
            else:
                offset = chars

            first_characters = buff.get_text (line_iter,
                                    buff.get_iter_at_offset (line_iter.get_offset() + offset),
                                    False)

            header_level = first_characters.count ('#') # Step 3

            if header_level > 0:
                if current_line not in self.heading_lines:
                    self.heading_lines.append (current_line)
                buff.remove_all_tags (line_iter, line_end_iter)
                buff.apply_tag (self.heading_tags [header_level - 1], line_iter, line_end_iter)
                buff.apply_tag (self.heading_margins [header_level - 1], line_iter, line_end_iter)
            else:
                if current_line in self.heading_lines:
                    self.heading_lines.remove (current_line)

    # This checks for bold, italics etc.
    def check_emphasis (self, buff, emphasis_type):

        start_iter = Gtk.TextIter ()
        end_iter = Gtk.TextIter ()

        start_iter = buff.get_start_iter ()
        end_iter = buff.get_end_iter ()

        text = buff.get_text (start_iter, end_iter, False)

        # Find all instances of the emphasis character we're checking for
        index = 0
        index_list = list ()

        while index != -1:
            index = text.find (emphasis_type, start_iter.get_offset (), end_iter.get_offset ())

            if index != -1:
                index_list.append (index)

            start_iter = buff.get_iter_at_offset (index + 1)

        # We have a list containing all indexes where there is an asterisk
        # There's probably an easier way to iterate over the list, I'm not good enough :P
        for i in range (0, len (index_list), 2): # For every pair in the list
            try:
                asterisk_start = buff.get_iter_at_offset (index_list[i])
                asterisk_end = buff.get_iter_at_offset (index_list[i + 1] + len(emphasis_type))
                buff.remove_all_tags (asterisk_start, asterisk_end)
                if emphasis_type == "*":
                    buff.apply_tag (self.italic, asterisk_start, asterisk_end)

                    mark = buff.create_mark (None, asterisk_start, True)
                    mark.set_visible (True)

                    end_mark = buff.create_mark (None, asterisk_end, True)
                    end_mark.set_visible (True)

                    self.single_asterisk_tags.append ((mark, end_mark))

                elif emphasis_type == "_":
                    buff.apply_tag (self.italic, asterisk_start, asterisk_end)

                    mark = buff.create_mark (None, asterisk_start, True)
                    mark.set_visible (True)

                    end_mark = buff.create_mark (None, asterisk_end, True)
                    end_mark.set_visible (True)

                if emphasis_type == "**":
                    buff.apply_tag (self.bold, asterisk_start, asterisk_end)

                    mark = buff.create_mark (None, asterisk_start, True)
                    mark.set_visible (True)

                    end_mark = buff.create_mark (None, asterisk_end, True)
                    end_mark.set_visible (True)

                    # First we need to delete the marks placed by the single asterisk check
                    for mark_pair in self.single_asterisk_tags:
                        iter_first = buff.get_iter_at_mark (mark_pair[0])
                        print (iter_first.get_offset ())
                        iter_second = buff.get_iter_at_mark (mark_pair[1])
                        print (iter_second.get_offset ())
                        print ("ASTERISK START OFFSET: " + str(asterisk_start.get_offset()) )
                        print ("ASTERISK END OFFSET: " + str(asterisk_end.get_offset()) )

                        print ("\n")
                        if buff.get_iter_at_mark (mark_pair[0]) == asterisk_start:
                            print ("MARK HAS BEEN PLACED HERE BEFORE")

                elif emphasis_type == "__":
                    buff.apply_tag (self.bold, asterisk_start, asterisk_end)

                    mark = buff.create_mark (None, asterisk_start, True)
                    mark.set_visible (True)

                    end_mark = buff.create_mark (None, asterisk_end, True)
                    end_mark.set_visible (True)

                if emphasis_type == "***":
                    buff.apply_tag (self.bold, asterisk_start, asterisk_end)
                    buff.apply_tag (self.italic, asterisk_start, asterisk_end)

                    mark = buff.create_mark (None, asterisk_start, True)
                    mark.set_visible (True)

                    end_mark = buff.create_mark (None, asterisk_end, True)
                    end_mark.set_visible (True)

            except IndexError: # Basically, there's a symbol which has no matching pair
                pass # this is probably a bad thing to do

    # We need to detect if a new line has been entered, and if list_mode is True,
    # then add a margin and the list symbol
    def check_lists (self, buff):
        for current_line in range (0, buff.get_line_count ()):
            line_iter = buff.get_iter_at_line (current_line)
            next_character = buff.get_text (line_iter, buff.get_iter_at_offset (line_iter.get_offset() + 1), False)
            if next_character == "-":
                self.in_list_mode = True
                line_end_iter = buff.get_iter_at_line (current_line)
                line_end_iter.forward_to_line_end ()

                buff.apply_tag (self.list_margin, line_iter, line_end_iter)
            else:
                self.in_list_mode = False

    # This is to check whether any tags were deleted and then reformat the text as necessary
        # TODO: Check for deletion of tags so that the text gets reformatted
        # Possibly by saving the positions of each tag pair and checking if any are deleted?
        # Try using Gtk.TextView.signals.delete_from_cursor
        # Use Gtk.TextMark maybe?
    def check_deletions (self, buff):
        pass
