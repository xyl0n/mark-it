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
            file_path = self.app_dir + filename
            file_object = open (file_path, 'r+')
            self.file_list.append (file_object)
            if filename[0:8] == "Untitled":
                self.untitled_count += 1

        self.file_list = self.sort_file_list (self.file_list)

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
            file_object = open (filepath, 'a+')
            self.file_list.append (file_object)
            self.file_list = self.sort_file_list (self.file_list)
            self.emit ("file-added", filename)
        except IOError as error:
            raise

    def get_file_object_from_name (self, name):
        for file_object in self.file_list:
            if self.path_to_name (file_object.name) == name:
                return file_object

        return None

    def get_index_of_file (self, name):
        for file_object in self.file_list:
            if self.path_to_name(file_object.name) == name:
                return self.file_list.index (file_object)

        return None

    def path_to_name (self, path):
        return path [len (self.app_dir):]

    def sort_file_list (self, file_list):
        name_list = list ()
        for file_object in file_list:
            name_list.append (file_object.name)

        name_list.sort ()

        sorted_list = list ()
        # Get the first name in the list
        for name in name_list:
            # Find the file object corresponding to it
            for file_object in file_list:
                if file_object.name == name:
                    sorted_list.insert (name_list.index (name), file_object)

        return sorted_list
