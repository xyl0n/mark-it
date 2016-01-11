public class MarkIt.FileObject {

    public string name = "";  
    
    public File file_obj;
    
    public FileObject (string path) {
         
         file_obj = File.new_for_path (path);
        
         var extension_index = path.last_index_of ("."); // Get the position of the dot where the file extension begins
         var name_index = path.last_index_of ("/"); // Get the position of the slash where the file name begins
         
         name = path.slice (name_index + 1, extension_index);   
    }  
    
    public void rename (string new_name) {
        
        var new_obj = file_obj.set_display_name (new_name + ".mkt");     
        file_obj = new_obj;    
        name = new_name;
    }
    
    public string read_contents () {
        
        string contents = "";
        
        try {
            var dis = new DataInputStream (file_obj.read ());
            string line;
            while ((line = dis.read_line (null)) != null) {
                contents += line + "\n";
            }
        } catch (Error e) {
            stdout.printf ("Error: %s\n", e.message);
        }
        
        return contents;
    }
    
    public void save (string contents) {
        
        var file_out = file_obj.replace (null, false, 0);                            
        file_out.write (contents.data);
    }
}
