public class MarkIt.Window : Gtk.Window  {
    
    TextView text_view;
    DocumentSidebar sidebar;
    DocumentManager documents;
    
    string app_folder;
    string data_folder;
    
    public Window () {
        
        set_default_size (1200, 800);
        
        var icon_theme = new Gtk.IconTheme ();
        set_icon_name ("accessories-text-editor");
        
        documents = new DocumentManager ();    
        
        build_ui ();
        
        this.destroy.connect (() => {
            Gtk.main_quit ();
        });
        
        app_folder = Environment.get_home_dir () + "/Documents/MarkIt/"; 
        data_folder = Environment.get_home_dir () + "/.local/share/mark-it/"; // Change to /usr/share in future
        
        try {
        
            var app_dir = File.new_for_path (app_folder);
            if (!app_dir.query_exists()) {
                app_dir.make_directory_with_parents ();
            }
            
            var data_dir = File.new_for_path (data_folder);
            if (!data_dir.query_exists()) {
                data_dir.make_directory_with_parents ();
            }
            
        } catch (Error e) {
            stdout.printf ("%s\n", e.message);
        }
    
        try {
            var css = new Gtk.CssProvider ();
            css.load_from_path (data_folder + "style.css");
        
            weak Gdk.Display display = Gdk.Display.get_default ();
            weak Gdk.Screen screen = display.get_default_screen ();
            get_style_context().add_provider_for_screen (screen, css, Gtk.STYLE_PROVIDER_PRIORITY_USER);
        } catch (Error e) {
            stdout.printf ("Error: %s\n", e.message);
        }    
    
    }
    
    private void build_ui () {
 
        // Top toolbar
        
        var header = new Gtk.HeaderBar ();
        header.set_show_close_button (true);
        //header.set_title ("MarkIt");
        set_titlebar (header);
        
        var title = new Gtk.Label ("MarkIt");
        var title_events = new Gtk.EventBox ();
        title_events.add (title);
        title.get_style_context().add_class ("title");
        
        var title_entry = new Gtk.Entry ();
        title_entry.set_placeholder_text ("Enter a new name");
        title_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, "go-jump-symbolic");
        title_entry.icon_press.connect (() => {
            title_entry.hide ();
            title_events.show_all ();
            
            if (title_entry.get_text () != "") {
                documents.rename_file (documents.current_file, title_entry.get_text());
            } else {
                
            }
        });
        
        var title_box = new Gtk.Box (Gtk.Orientation.HORIZONTAL, 0);
        title_box.pack_start (title_entry);
        title_box.pack_start (title_events);
        header.set_custom_title (title_box);
        
        title_events.button_press_event.connect ((event_button) => {
            if (event_button.type == Gdk.EventType.DOUBLE_BUTTON_PRESS) {
                title_events.hide ();
                title_entry.show_all ();
            }
            title_entry.set_text (documents.current_file.name);
             
            return true;
        });
        

        var new_button = new Gtk.Button.from_icon_name ("document-new-symbolic", Gtk.IconSize.SMALL_TOOLBAR);        
        header.pack_start (new_button);
        
        new_button.clicked.connect (() => {
        
            string name = "Untitled";
            bool num_found = false;
            int num = 1;
            while (!num_found) {
                string name_with_num = name + " " + num.to_string (); 
                if (!documents.file_exists (name_with_num)) {
                    name = name_with_num;
                    num_found = true;
                } else {
                    num++;
                }
            }
            
            documents.create_file (name);
        });
    
        // The main text view
    
        text_view = new TextView ();
        this.configure_event.connect (() => {
        
            int parent_w = text_view.get_parent ().get_allocated_width ();
        
            text_view.set_margin_start ((parent_w / 2) - (text_view.get_allocated_width() / 2));
            text_view.set_margin_end ((parent_w / 2) - (text_view.get_allocated_width () / 2));
            
            return false;
        });
        
      
        var text_scrolled = new Gtk.ScrolledWindow (null, null);
        
        text_scrolled.set_policy (Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC);
        text_scrolled.add (text_view);
        text_scrolled.get_style_context().add_class ("view");
        
        // Document sidebar
        
        sidebar = new DocumentSidebar (documents);
        documents.current_file_changed.connect ((file) => {
            text_view.get_buffer ().set_text (file.read_contents());
            title.set_label (file.name);

            sidebar.set_current_file (file);
        });
        
        documents.file_list_changed.connect ((file) => {
            sidebar.update_file_list (documents);
        });
        
        documents.workspace_list_changed.connect (() => {
            stdout.printf ("Workspace changed!\n");
            sidebar.update_workspace_list (documents);
        });
        
        // Autosave
        text_view.get_buffer ().changed.connect (() => {
        
            Gtk.TextIter start, end;
            var buff = text_view.get_buffer ();
            buff.get_bounds (out start, out end);
            var text = buff.get_text (start, end, false);
            
            documents.current_file.save (text);  
        });
        
        // Paned
        
        var paned = new Gtk.Paned (Gtk.Orientation.HORIZONTAL);
        paned.add1 (sidebar);
        paned.add2 (text_scrolled);
        
        add (paned);
        
        this.show_all ();
        title_entry.hide ();
    }
}
