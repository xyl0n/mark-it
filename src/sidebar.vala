public class MarkIt.DocumentSidebar : Gtk.Box  {

    Gtk.TreeStore files_store;            
    Gtk.TreeView document_view;
    Gtk.TreeView workspace_view;
    
    public signal void file_open_request (List<FileObject> file_list);
    
    public DocumentSidebar (DocumentManager manager) {
    
        set_orientation (Gtk.Orientation.VERTICAL);
        get_style_context ().add_class ("markit-sidebar");
        get_style_context ().add_class ("view");
        get_style_context ().add_class ("sidebar");
    
        set_size_request (200, -1);        
        
        var workspace_label = new Gtk.Label ("<b>Workspace</b>");
        workspace_label.set_use_markup (true);
        workspace_label.get_style_context().add_class ("dim-label");
        workspace_label.set_alignment (0.0f, 0.5f);
        workspace_label.margin = 6;
        workspace_label.margin_left = 12;
        
        pack_start (workspace_label, false);
        setup_workspace_tree (manager);
        
        var doc_label = new Gtk.Label ("<b>Documents</b>");
        doc_label.set_use_markup (true);
        doc_label.get_style_context().add_class ("dim-label");
        doc_label.set_alignment (0.0f, 0.5f);
        doc_label.margin = 6;
        doc_label.margin_left = 12;
        
        pack_start (doc_label, false);
        
        setup_document_tree (manager);
	}
	
	private void setup_document_tree (DocumentManager manager) {
	
	    document_view = new Gtk.TreeView ();
        document_view.get_style_context().add_class ("markit-document-view");
        
        Gtk.TreeStore store = new Gtk.TreeStore (2, typeof (string), typeof (string));
		document_view.set_model (store);
		
		document_view.insert_column_with_attributes (-1, "Product", new Gtk.CellRendererText (), "text", 0, null);
        document_view.set_headers_visible (false);
        document_view.set_activate_on_single_click (true);
        //document_view.get_selection ().set_mode (Gtk.SelectionMode.NONE);

		Gtk.TreeIter root;
		Gtk.TreeIter file_iter;

		//store.append (out root, null);
		//store.set (root, 0, "Workspace", -1);

        if (manager.file_list.length () > 0) {
		//    store.append (out root, null);
		//    store.set (root, 0, "Documents", -1);
		//}
		
            for (int list_iter = 0; list_iter < manager.file_list.length (); list_iter++) {
                store.append (out root, null);
		        store.set (root, 0, manager.file_list.nth_data(list_iter).name, -1);
            }
        }
        
        document_view.row_activated.connect ((row_path, row_column) => {
            var selection = document_view.get_selection ();
	        Gtk.TreeModel model;
	    
    	    var path_list = selection.get_selected_rows (out model);
	        List<FileObject> file_list = new List<FileObject> ();
	        path_list.foreach ((path) => {
	            Gtk.TreeIter iter;
	            model.get_iter (out iter, path);
	            Value val;
	            model.get_value (iter, 0, out val);
	            FileObject? file = manager.get_file_by_name (val.get_string());    
	            
	            if (!manager.file_opened (file)) {
	                file_list.append (file);
	                manager.open_files (file_list);
	            }
	        });
        });
        
        pack_start (document_view, false);      
	}
	
	private void setup_workspace_tree (DocumentManager manager) {
	
	    workspace_view = new Gtk.TreeView ();
        
        Gtk.TreeStore store = new Gtk.TreeStore (2, typeof (string), typeof (string));
		workspace_view.set_model (store);
		
		workspace_view.insert_column_with_attributes (-1, "File", new Gtk.CellRendererText (), "text", 0, null);
        workspace_view.set_headers_visible (false);
        workspace_view.set_activate_on_single_click (true);
        document_view.get_selection ().set_mode (Gtk.SelectionMode.BROWSE);

		Gtk.TreeIter root;

        if (manager.workspace_list.length () > 0) {

            for (int list_iter = 0; list_iter < manager.workspace_list.length (); list_iter++) {
                store.append (out root, null);
		        store.set (root, 0, manager.workspace_list.nth_data(list_iter).name, -1);
            }
        }
        
        workspace_view.row_activated.connect ((row_path, row_column) => {
            var selection = workspace_view.get_selection ();
	        Gtk.TreeModel model;
	    
    	    var path_list = selection.get_selected_rows (out model);
	        FileObject? file = new FileObject (null);
	        path_list.foreach ((path) => {
	            Gtk.TreeIter iter;
	            model.get_iter (out iter, path);
	            Value val;
	            model.get_value (iter, 0, out val);
	            
	            file = manager.get_file_by_name (val.get_string());
	        });
	    	    
	        manager.set_current_file (file);
        });
        
        pack_start (workspace_view, false);      
	}
	
	public void update_file_list (DocumentManager manager) {
	    
	    var store = (Gtk.TreeStore) document_view.get_model ();
	    store.clear ();
	    
	    Gtk.TreeIter root;
	    
	    if (manager.file_list.length () > 0) {
		
            for (int list_iter = 0; list_iter < manager.file_list.length (); list_iter++) {
                store.append (out root, null);
		        store.set (root, 0, manager.file_list.nth_data(list_iter).name, -1);
            }
        }
	}
	
	public void update_workspace_list (DocumentManager manager) {
	    
	    var store = (Gtk.TreeStore) workspace_view.get_model ();
	    store.clear ();
	    	
	    Gtk.TreeIter root; 	
	    	    
	    if (manager.workspace_list.length () > 0) {
		
            for (int list_iter = 0; list_iter < manager.workspace_list.length (); list_iter++) {
                store.append (out root, null);
		        store.set (root, 0, manager.workspace_list.nth_data(list_iter).name, -1);
            }
        }
        
        workspace_view.set_model (store);
	}
	
	public void set_current_file (FileObject file) {
	    
	    workspace_view.get_model ().foreach ((model, path, iter) => {
	   
	        Value val;
	        model.get_value (iter, 0, out val);
	        if (file.name == (string)val) {
	            workspace_view.set_cursor (path, null, false);
	        }
	            
	        stdout.printf ("%s\n", (string)val);   
	        
	        return false;
	    });
	}
}
