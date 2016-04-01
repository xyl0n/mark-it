#!/usr/bin/env python

import os
import errno

from gi.repository import GObject

import threading
import shutil
from enum import IntEnum
from collections import deque

class MarkItFileObject:

    # This class carries information about a file or a folder

    def __init__ (self, name, path, is_folder = False, parent_folder = None):
        self.name = name
        self.parent_folder = parent_folder
        self.parent_folder_obj = None
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

    def get_file_object (self):
        return self.file_obj

    def get_is_folder (self):
        return self.is_folder

    def get_path (self):
        return self.path

    def set_path (self, path):
        self.path = path

    def get_is_open (self):
        return self.is_open

    def set_parent_folder_obj (self, folder_obj):
        self.parent_folder_obj = folder_obj

    def get_parent_folder_obj (self):
        return self.parent_folder_obj

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
        'file_renamed': (GObject.SIGNAL_RUN_FIRST, None, (str, str, str,)),
        'folder_created': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'folder_moved': (GObject.SIGNAL_RUN_FIRST, None, (str, str,)),
        'folder_renamed': (GObject.SIGNAL_RUN_FIRST, None, (str, str, str,)),
        'file_moved': (GObject.SIGNAL_RUN_FIRST, None, (str, str,)),
    }

    FileTypes = IntEnum ('FileTypes', 'FILE FOLDER')

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
                parent_dir = root + "/"
                if root == self.app_dir:
                    parent_dir = None

                if root[-1:] != "/":
                    file_path = root + "/" + directory + "/"
                else:
                    file_path = root + directory + "/"

                folder_obj = MarkItFileObject (directory, file_path,
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

                parent_dir = root + "/"
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

        for file_obj in self.file_list:
            index = file_obj.get_path ().rfind ("/")
            parent_path = file_obj.get_path ()[:index] + "/"
            if parent_path != self.app_dir:
                folder_obj = self.get_file_object_from_path (parent_path, is_folder = True)
                file_obj.set_parent_folder_obj (folder_obj)
            else:
                file_obj.set_parent_folder_obj (None)

        for folder_obj in self.folder_list:
            index = folder_obj.get_path ().rfind ("/")
            index = folder_obj.get_path ()[:index].rfind ("/")
            parent_path = folder_obj.get_path ()[:index] + "/"
            if parent_path != self.app_dir:
                parent_folder_obj = self.get_file_object_from_path (parent_path, is_folder = True)
                folder_obj.set_parent_folder_obj (parent_folder_obj)
            else:
                folder_obj.set_parent_folder_obj (None)

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
            self.emit ("file_created", file_path)
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

    def move_folder (self, old_path, new_path):

        shutil.move(old_path, new_path)
        folder_obj = self.get_file_object_from_path (old_path, is_folder = True)

        old_folder_paths = {}

        for child_folder in self.folder_list:
            if child_folder.get_path () != old_path: # So if its not the same folder
                levels = self.folder_is_ancestor (folder_obj, child_folder)
                if levels != 0:
                    child = child_folder
                    hierarchy = deque ()
                    for i in range (0, levels):
                        hierarchy.appendleft (child.get_name ())
                        parent = child_folder.get_parent_folder_obj ()
                        if parent.get_path () != old_path:
                            child = parent

                    child_path = new_path
                    for item in hierarchy:
                        child_path += "/"
                        child_path += item

                    child_path += "/"
                    old_folder_paths[child_folder.get_path ()] = child_folder
                    child_folder.set_path (child_path)

        for file_obj in self.file_list:
            # Change the path for files which are a descendant of the folder
            levels = self.folder_is_ancestor (folder_obj, file_obj)
            if levels != 0:
                child = file_obj
                hierarchy = deque ()
                for i in range (0, levels):
                    hierarchy.appendleft (child.get_name ())
                    parent = file_obj.get_parent_folder_obj ()
                    if parent.get_path () != old_path:
                        child = parent

                child_path = new_path
                for item in hierarchy:
                    child_path += "/"
                    child_path += item

                file_obj.set_path (child_path)
                '''
                for old_path in old_folder_paths:
                    if file_obj.get_parent_folder_obj ().get_path () == old_path:
                        pass
                '''

        folder_obj.set_path (new_path)
        self.emit ("folder_moved", old_path, new_path)

    def move_file (self, old_path, new_path):
        shutil.move(old_path, new_path)

        folder_obj = self.get_file_object_from_path (old_path, is_folder = False)
        folder_obj.set_path (new_path)

        self.emit ("file_moved", old_path, new_path)

    def rename_file (self, file_path, new_name):
        # FIXME: We need to do checks whether the file already exists, if it's a
        # directory etc.
        file_obj = self.get_file_object_from_path (file_path)
        index_without_name = file_obj.get_path().rfind (file_obj.get_name())
        new_file_path = file_obj.get_path()[:index_without_name] + new_name
        old_name = file_obj.get_name ()
        file_obj.set_path (new_file_path)
        file_obj.set_name (new_name)

        os.rename (file_path, new_file_path)

        self.emit ("file_moved", file_path, new_file_path)
        self.emit ("file_renamed", file_path, old_name, new_name)

    def get_file_object_from_path (self, path, is_folder = False):
        if is_folder != True:
            for file_object in self.file_list:
                print ("From get_file_object_from_path, file path is " + file_object.get_path ())
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

    def get_children_of_folder (self, folder_obj):
        # Gets the direct children of a folder
        children = list ()
        for file_obj in self.file_list:
            levels = self.folder_is_ancestor (folder_obj, file_obj)
            if levels == 1:
                children.append (file_obj)

        for child_folder_obj in self.folder_list:
            levels = self.folder_is_ancestor (folder_obj, child_folder_obj)
            if levels == 1:
                children.append (child_folder_obj)

        return children

    def path_to_name (self, path, is_folder = False):
        file_obj = self.get_file_object_from_path (path, is_folder = is_folder)
        if file_obj != None:
            return file_obj.get_name ()

        return None

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

    def folder_is_ancestor (self, ancestor_folder_obj, child):
        # Child may be a folder or a file
        # Recursively get the parent of the file until the parent is the root directory

        levels = 0

        parent_is_root = False
        while parent_is_root == False:
            parent = child.get_parent_folder_obj ()
            if parent == None:
                parent_is_root = True
            else:
                levels += 1
                if parent.get_path () == ancestor_folder_obj.get_path ():
                    return levels # Return how deeply descended the file is

                child = parent

        return 0
