#!/usr/bin/env python

import os
import errno

from gi.repository import GObject

import threading

class MarkItFileObject (GObject.GObject):

    # This class carries information about a file or a folder

    def __init__ (self, name, path, is_folder = False, parent_folder = None):
        self.name = name
        self.parent_folder = parent_folder
        self.is_folder = is_folder
        self.file_obj = None
        self.path = path

        self.is_open = False

    def get_name (self):
        return self.name

    def open_file (self):
        if self.is_folder == False:
            try:
                # Try to create the file and open it for read/write
                self.file_obj = open(self.path, "x+")
                self.is_open = True
            except FileExistsError:
                # If the file exists then we can do a read/write starting from the
                # beginning of the file
                self.file_obj = open (self.path, "r+")
                self.is_open = True

    def set_name (self, name):
        self.name = name

    def get_parent_folder (self):
        return self.parent_folder

    def set_parent_folder (self, parent_folder):
        self.parent_folder = parent_folder

    def get_file_object (self):
        return self.file_obj

    def get_is_folder (self):
        return self.is_folder

    def get_path (self):
        return self.path

    def get_is_open (self):
        return self.is_open

    def close (self):
        self.file_obj.close ()
        self.is_open = False

class MarkItFileManager (GObject.GObject):

    # This class is made to load, create and delete files which have been produced
    # by mark it
    # Files are saved in Documents/MarkIt
    # On start up, we want to load a list of all the files we have by scanning the
    # folder and getting the file names
    # These are then displayed on the file sidebar

    __gsignals__ = {
        'file_created': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'file_deleted': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'file_opened': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'file_closed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'folder_created': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }

    def __init__ (self, open_files):
        # If this is the first run, we won't have a directory, so lets try to
        # create one if it doesn't exist
        GObject.GObject.__init__ (self)
        self.app_dir = os.path.expanduser ("~") + "/Documents/MarkIt/"
        self.file_count = 0
        self.untitled_count = 0
        self.folder_count = 0
        try:
            os.makedirs (self.app_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        # Now we recursively get all the files and folders in the directory
        self.file_list = list ()
        self.folder_list = list ()

        for root, dirs, filenames in os.walk (self.app_dir):
            for directory in dirs:
                # Add the folder to our list
                parent_dir = root[len(self.app_dir):]
                if root == self.app_dir:
                    parent_dir = None
                folder_obj = MarkItFileObject (directory, root + "/" + directory,
                                               is_folder = True,
                                               parent_folder = parent_dir)
                self.folder_list.append (folder_obj)
                os.path.join (root, directory)
            for filename in filenames:
                self.file_count += 1
                if root[-1:] != "/":
                    file_path = root + "/" + filename
                else:
                    file_path = root + filename

                parent_dir = root[len(self.app_dir):]
                if root == self.app_dir:
                    parent_dir = None
                file_object = MarkItFileObject (filename, file_path,
                                                is_folder = False,
                                                parent_folder = parent_dir)
                self.file_list.append (file_object)
                if filename[0:8] == "Untitled":
                    self.untitled_count += 1

        self.file_list = self.sort_file_list (self.file_list)
        self.folder_list = self.sort_file_list (self.folder_list)

        # Open the file so we can I/O
        self.open_files = list ()
        for file_path in open_files:
            self.open_file (file_path)

    def get_file_list (self):
        return self.file_list

    def get_folder_list (self):
        return self.folder_list

    def get_app_dir (self):
        return self.app_dir

    def get_open_files (self):
        return self.open_files

    def close_file (self, path):
        file_obj = self.get_file_object_from_path (path)
        if file_obj.get_is_open () == True:
            while threading.activeCount() > 1:
                pass
            else:
                file_obj.close ()

            self.emit ("file_closed", path)

        self.open_files.remove (file_obj)

    # IMPORTANT: Always use this function to open a file instead of accessing
    # the file object directly since we need to emit the file_opened signal
    def open_file (self, path):
        if path[-1:] == "/":
            path = path[:-1] # Just remove any trailing forward slashes

        file_obj = self.get_file_object_from_path (path)

        if file_obj.get_is_open () != True:
            file_obj.open_file ()
            self.open_files.append (file_obj)
            self.emit ("file_opened", path)

    def create_new_file (self):
        self.untitled_count += 1
        self.file_count += 1
        filename = "Untitled " + str (self.untitled_count)
        file_path = self.app_dir + filename

        try:
            file_object = MarkItFileObject (filename, file_path)
            self.file_list.append (file_object)
            self.file_list = self.sort_file_list (self.file_list)
            self.open_file (file_path)
            self.emit ("file_created", filename)
        except IOError as error:
            raise

    def create_new_folder (self, folder_name):
        # Make new folder
        # For some reason that probably made sense at the time we create the
        # folder here, the object does not create it
        try:
            path = self.app_dir + folder_name
            os.makedirs (path)

            folder_obj = MarkItFileObject (folder_name, self.app_dir + folder_name, is_folder = True)
            self.folder_list.append (folder_obj)

            self.emit ("folder_created", path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def get_file_object_from_name (self, name):
        for file_object in self.file_list:
            if file_object.get_name () == name:
                return file_object

        return None

    def get_file_object_from_path (self, path, is_folder = False):

        if is_folder != True:
            for file_object in self.file_list:
                if file_object.get_path () == path:
                    return file_object
        else:
            for folder_object in self.folder_list:
                if folder_object.get_path () == path:
                    return folder_object

        return None

    def get_index_of_file (self, name):
        for index, file_obj in enumerate (self.file_list):
            if file_obj.get_name () == name:
                return index

        return 0

    def path_to_name (self, path):
        file_obj = self.get_file_object_from_path (path)
        return file_obj.get_name ()

    def sort_file_list (self, file_list):
        name_list = list ()
        for file_object in file_list:
            name_list.append (file_object.get_name ())

        name_list.sort ()

        sorted_list = list ()
        # Get the first name in the list
        for name in name_list:
            # Find the file object corresponding to it
            for file_object in file_list:
                if file_object.get_name () == name:
                    sorted_list.insert (name_list.index (name), file_object)

        return sorted_list
