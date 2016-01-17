#!/usr/bin/env python

import os
import errno

from gi.repository import GObject

class MarkItFileManager (GObject.GObject):

    # This class is made to load, create and delete files which have been produced
    # by mark it
    # Files are saved in Documents/MarkIt
    # On start up, we want to load a list of all the files we have by scanning the
    # folder and getting the file names
    # These are then displayed on the file sidebar

    __gsignals__ = {
        'file-added': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'file-removed': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__ (self):
        # If this is the first run, we won't have a directory, so lets try to
        # create one if it doesn't exist
        GObject.GObject.__init__ (self)
        self.app_dir = os.path.expanduser ("~") + "/Documents/MarkIt/"
        self.file_count = 0
        self.untitled_count = 0
        try:
            os.makedirs (self.app_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        # Now we get all the files in the directory
        self.file_list = list ()

        for filename in os.listdir (self.app_dir):
            self.file_count += 1
            self.file_list.append (filename)
            if filename[0:8] == "Untitled":
                self.untitled_count += 1

        self.file_list.sort ()

    def get_file_list (self):
        return self.file_list

    def get_app_dir (self):
        return self.app_dir

    def create_new_file (self):
        self.untitled_count += 1
        self.file_count += 1
        filename = "Untitled " + str (self.untitled_count)
        filepath = self.app_dir + filename

        try:
            open (filepath, 'a')
            self.file_list.append (filename)
            self.file_list.sort ()
            self.emit ("file-added", filename)
        except IOError as error:
            raise
