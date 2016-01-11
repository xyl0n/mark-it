public class MarkIt.TextView : Gtk.SourceView {
  
    Gtk.TextTag first_heading;
    Gtk.TextTag second_heading;
    Gtk.TextTag third_heading;
    Gtk.TextTag bold;
    Gtk.TextTag italic;
  
    public TextView () {
        
        set_wrap_mode (Gtk.WrapMode.WORD_CHAR);
        left_margin = 24;
        right_margin = 24;   
        set_auto_indent (true);
        set_highlight_current_line (true);
        set_indent_on_tab (true);
        set_indent_width (4);
        set_insert_spaces_instead_of_tabs (true);
        set_tab_width (4);
        
        var buff = get_buffer ();

        buff.changed.connect (on_text_changed);
        buff.insert_text.connect (on_text_insert);

        var settings = new Settings("org.gnome.desktop.interface");
        var font_name = settings.get_string("monospace-font-name");
        var font_desc = Pango.FontDescription.from_string (font_name);
        override_font (font_desc);  // In the future, have an option to change from sans to mono
        
        first_heading = buff.create_tag ("first_heading", "weight", Pango.Weight.SEMIBOLD, 
                                 "scale", Pango.Scale.X_LARGE);
        second_heading = buff.create_tag ("second_heading", "weight", Pango.Weight.MEDIUM, 
                                         "scale", Pango.Scale.LARGE);     
        third_heading = buff.create_tag ("third_heading", "weight", Pango.Weight.MEDIUM, 
                                         "style", Pango.Style.ITALIC,
                                         "scale", Pango.Scale.LARGE);                
        bold = buff.create_tag ("bold", "weight", Pango.Weight.BOLD);
        italic = buff.create_tag ("italic", "style", Pango.Style.ITALIC);
    
        this.key_press_event.connect (on_key_press);
    }
    
    
    public override void size_allocate (Gtk.Allocation allocation) {

        allocation.width = 800;
        base.size_allocate (allocation);  
    }    
    
    void on_text_changed () {
        
        var buff = get_buffer ();
        
        for (int line_count = 0; line_count < buff.get_line_count (); line_count++) {
            
            Gtk.TextIter line_iter;
            buff.get_iter_at_line (out line_iter, line_count);
            
            check_headings (buff, line_iter);            
        }
        
        check_emphasis (buff, "*");
        check_emphasis (buff, "**");
        check_emphasis (buff, "_");
        check_emphasis (buff, "__");
    }
    
    bool on_key_press (Gdk.EventKey event) {
    
        return false;       
    }
    
    void on_text_insert (ref Gtk.TextIter pos, string new_text, int new_text_length) {
        
    }
    
    void check_headings (Gtk.TextBuffer buff, Gtk.TextIter line_iter) {
            
        // Checking for headings
        var iter_next = line_iter;
        iter_next.forward_char ();
            
        if (buff.get_text (line_iter, iter_next, false) == "#") {
            
            var iter_end = line_iter;
            iter_end.forward_to_line_end ();
            
            buff.remove_all_tags (line_iter, iter_end);
            buff.apply_tag (first_heading, line_iter, iter_end);
        }
                            
        iter_next.forward_char ();
        if (buff.get_text (line_iter, iter_next, false) == "##") {
                
            var iter_end = line_iter;
            iter_end.forward_to_line_end ();
            
            buff.remove_all_tags (line_iter, iter_end);
            buff.apply_tag (second_heading, line_iter, iter_end);
        }
            
        iter_next.forward_char ();
        if (buff.get_text (line_iter, iter_next, false) == "###") {
            
            var iter_end = line_iter;
            iter_end.forward_to_line_end ();
            
            buff.remove_all_tags (line_iter, iter_end);
            buff.apply_tag (third_heading, line_iter, iter_end);
        }
            
    }
    
    void check_emphasis (Gtk.TextBuffer buff, string emphasis_type) {
        
        // Get ALL the text
        Gtk.TextIter start_iter, end_iter;
        buff.get_start_iter (out start_iter);
        buff.get_end_iter (out end_iter);
        
        string doc_text = buff.get_text (start_iter, end_iter, false);       
        
        int last_occur = get_number_of_occurences (doc_text, emphasis_type);
        int start_index = 0;
        
        int pair_occur = last_occur / 2; // Get the number of pairs, discarding the 
                                         // last character if there is an odd number
        
        for (int i = 0; i < pair_occur; i++) {
                        
            int[] positions = find_emphasis_pair (doc_text, emphasis_type, start_index);
            Gtk.TextIter emphasis_start, emphasis_end;
            buff.get_iter_at_offset (out emphasis_start, positions[0]);
            buff.get_iter_at_offset (out emphasis_end, positions[1]);   

            emphasis_end.forward_chars (emphasis_type.length);
        
            buff.remove_all_tags (emphasis_start, emphasis_end);
            if (emphasis_type == "*" ||
                emphasis_type == "_") {
                buff.apply_tag (italic, emphasis_start, emphasis_end);
            } else if (emphasis_type == "**" ||
                       emphasis_type == "__") {
                buff.apply_tag (bold, emphasis_start, emphasis_end);
            }
          
            start_index = positions[1] + emphasis_type.length;
        }  
    }
    
    // Function to find the positions of an emphasis pair within the text
    
    int[] find_emphasis_pair (string text, string emphasis_type, int start_index) {
        
        int opening = text.index_of (emphasis_type, start_index);
        int closing = text.index_of (emphasis_type, opening + emphasis_type.length);
        
        return {opening, closing};     
    }
    
    int get_number_of_occurences (string text, string search_string) {
        
        var occur = 0;
        var pos = 0;
        
        var step = search_string.length;

        while(true) {
        
            pos = text.index_of (search_string, pos);
            if(pos >= 0) { 
                occur++; 
                pos += step; 
            } else break;
        }
                
        return occur;
    }
}
