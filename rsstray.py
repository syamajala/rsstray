from gi.repository import Gtk, GObject, Gdk
from gi.repository import Notify
import feedparser
import webbrowser
import threading
        
class aStatusIcon:
    
    def __init__(self, feeds):
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file("rss.jpg")
        self.statusicon.connect("popup-menu", self.right_click_event)        
        self.updates = dict()
        self.menu = Gtk.Menu()
        
        for i in feeds:
            self.updates[i[0]] = threading.Timer(i[1], self.update, args=[i[0]])
            self.updates[i[0]].start()

        about = Gtk.MenuItem()
        about.set_label("About")

        quit = Gtk.MenuItem()
        quit.set_label("Quit")

        about.connect("activate", self.show_about_dialog)
        quit.connect("activate", self.quit)
        
        self.menu.append(about)
        self.menu.append(quit)

    def open_browser(self, url):
        def open_url(self):
            webbrowser.open(url)
        return open_url
        
    def build_submenu(self, feed):
        menu = Gtk.Menu()

        for i in feed.entries:
            menuitem = Gtk.MenuItem()
            menuitem.set_label(i.title)
            menuitem.connect("activate", self.open_browser(i.link))
            menu.append(menuitem)

        return menu
        
    def update(self, url):                
        pfeed = feedparser.parse(url)

        feed = Gtk.MenuItem()
        feed.set_label(pfeed.feed.title)
        feed.set_submenu(self.build_submenu(pfeed))

        self.menu.append(feed)

        Notify.Notification.new(pfeed.feed.title, str(len(pfeed.entries)) + " new articles", "dialog-information").show()
        
    def right_click_event(self, icon, button, time):
        self.menu.show_all()

        def pos(menu, icon):
            return (Gtk.StatusIcon.position_menu(menu, icon))

        self.menu.popup(None, None, pos, self.statusicon, button, time) 

    def quit(self, arg):
        for i in self.updates.values():
            i.cancel()
        
        Gtk.main_quit
        
    def show_about_dialog(self, widget):
        about_dialog = Gtk.AboutDialog()

        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name("RSS Tray")
        about_dialog.set_version("0.1")
        about_dialog.set_authors(["Seshu Yamajala"])

        about_dialog.run()
        about_dialog.destroy()

if __name__ == '__main__':
    GObject.threads_init()
    Gdk.threads_init()
    Notify.init('RSS Tray')
    aStatusIcon([('http://www.osnews.com/files/recent.xml', 10), ('http://feeds.arstechnica.com/arstechnica/index?format=xml', 10)])
    Gtk.main()
