public class MarkIt.DocumentManager {
    
    string dir_path;
    File app_folder;
        
    public List<FileObject> file_list;    
    public List<FileObject> workspace_list; 
    
    public FileObject current_file;
        
    public signal void current_file_changed (FileObject new_file);     
    public signal void file_list_changed (); 
    public signal void workspace_list_changed ();  
         
    public DocumentManager () {
        
        dir_path = Environment.get_home_dir () + "/Documents/MarkIt/";    
        file_list = new List<FileObject> ();
        workspace_list = new List<FileObject> ();
        
        try {
        
            app_folder = File.new_for_path (dir_path);
            if (!app_folder.query_exists()) {
                app_folder.make_directory_with_parents ();
            }        
            
            var dir = Dir.open (dir_path);
            
            string filename;
            while ((filename = dir.read_name()) != null) {
                var temp_file = new FileObject (dir_path + filename);
                file_list.append (temp_file);
            }
                
            file_list.sort (strcmp);    // ??
        } catch (Error e) {
            stdout.printf ("%s\n", e.message);
        }        
    }
    
    public void open_files (List<FileObject> file_list) {
        
        file_list.foreach ((file) => {
            workspace_list.append (file);
        });
        
        set_current_file (file_list.nth_data (0));
        workspace_list_changed ();
    }
    
    public void create_file (string name) {
        
        string path = dir_path + name + ".mkt";
        
        var new_file = new FileObject (path);
        if (!new_file.file_obj.query_exists()) {
            try {
		        new_file.file_obj.create (FileCreateFlags.PRIVATE);
	        } catch (Error e) {
		        stdout.printf ("Error: %s\n", e.message);
	        }
	        
	        set_current_file (new_file);
	        file_list.append (new_file);
	        file_list_changed ();
	        workspace_list.append (new_file);
	        workspace_list_changed ();
        } else {
            stdout.printf ("File already exists\n");
        }
    }
    
    public void rename_file (FileObject file, string new_name) {
        
        // Rename the file in the index
        int index = file_list.index (get_file_by_name (file.name));
        file_list.remove (file);
        file.rename (new_name);
        file_list.insert (file, index);
        file_list_changed ();
        current_file_changed (file);
        workspace_list_changed ();
    }
    
    public FileObject? get_file_by_name (string name) {
        
        FileObject? _file = null;
        
        file_list.foreach ((file) => {
            if (file.name == name) {
                _file = file;
            }
        });

        return _file;
    }   
    
    public bool file_exists (string name) {
        var temp_file = new FileObject (dir_path + name + ".mkt");
        if (temp_file.file_obj.query_exists ()) {
            return true;
        }
        
        return false;
    }
    
    public bool file_opened (FileObject file) {
        if (workspace_list.index(file) != -1) {
            return true;
        }
        
        return false;
    }
    
    public void set_current_file (FileObject new_file) {
        current_file = new_file;
        current_file_changed (current_file);
    } 
    
}
