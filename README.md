Mark It is a markdown editor for Linux (maybe Windows) systems.

REQUIREMENTS
------------
You need:
* python (3.0 or above)
* gtk (anything above 3.10 should work)

INSTALLATION
------------
Not entirely sure how to distribute python apps, you need to run the following though:

# cp ./org.gnome.mark-it.gschema.xml /usr/share/glib-2.0/schemas
# glib-compile-schemas /usr/share/glib-2.0/schemas

Then you can run the app by doing
$ python3 ./main.py
