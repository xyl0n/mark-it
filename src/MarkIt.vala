public class MarkIt.MarkIt : GLib.Object  {
    
    public MarkIt () {
        
        //Gtk.Settings.get_default().set("gtk-application-prefer-dark-theme", true);
        var window = new Window ();
    
    }
        
    public static int main (string[] argv) {
        
        Gtk.init (ref argv);
        
        var app = new MarkIt ();
        
        Gtk.main ();
        
        return 0;
    }
}
