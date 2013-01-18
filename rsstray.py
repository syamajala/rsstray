from gi.repository import Gtk
from gi.repository import Notify
import feedparser
import webbrowser
        
class aStatusIcon:
    
    def __init__(self):
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file("rss.jpg")
        self.statusicon.connect("popup-menu", self.right_click_event)
        Notify.init('RSS Tray')
        self.d = feedparser.parse('http://www.osnews.com/files/recent.xml')
        
    def right_click_event(self, icon, button, time):
        self.menu = Gtk.Menu()

        about = Gtk.MenuItem()
        about.set_label("About")

        feed1 = Gtk.MenuItem()
        feed1.set_label(self.d.feed.title)
        feed1.set_submenu(self.build_submenu(self.d))
        
        quit = Gtk.MenuItem()
        quit.set_label("Quit")

        about.connect("activate", self.show_about_dialog)
        quit.connect("activate", Gtk.main_quit)
        
        self.menu.append(about)
        self.menu.append(feed1)
        self.menu.append(quit)

        self.menu.show_all()

        def pos(menu, icon):
            return (Gtk.StatusIcon.position_menu(menu, icon))

        self.menu.popup(None, None, pos, self.statusicon, button, time) 

    def build_submenu(self, feed):
        menu = Gtk.Menu()

        for i in feed.entries:
            menuitem = Gtk.MenuItem()
            menuitem.set_label(i.title)
            menuitem.connect("activate", lambda x: webbrowser.open(i.link))
            menu.append(menuitem)

        return menu
        
    def show_about_dialog(self, widget):
        about_dialog = Gtk.AboutDialog()

        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name("StatusIcon Example")
        about_dialog.set_version("1.0")
        about_dialog.set_authors(["Andrew Steele"])

        about_dialog.run()
        about_dialog.destroy()

aStatusIcon()
Gtk.main()
