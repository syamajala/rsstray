#!/usr/bin/python
from gi.repository import Gtk, GObject, Gdk
from gi.repository import Notify
import feedparser
import webbrowser
import threading
import sched
import time
        
class aStatusIcon:
    
    def __init__(self, feeds):
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file("rss.jpg")
        self.statusicon.connect("popup-menu", self.right_click_event)        
        self.menu = Gtk.Menu()
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.feeds = feeds
        
        about = Gtk.MenuItem()
        about.set_label("About")

        quit = Gtk.MenuItem()
        quit.set_label("Quit")

        about.connect("activate", self.show_about_dialog)
        quit.connect("activate", Gtk.main_quit)
        
        self.menu.append(about)
        self.menu.append(quit)

        for i in feeds:
            self.update(i)

        self.schedthread = threading.Thread(target=self.scheduler.run, daemon=True)
        self.schedthread.start()
        
    def build_submenu(self, feed):
        menu = Gtk.Menu()

        for i in feed.entries:
            menuitem = Gtk.MenuItem()
            menuitem.set_label(i.title)
            menuitem.link = i.link
            menuitem.connect("activate", lambda x: webbrowser.open(x.link))
            menu.append(menuitem)

        return menu
        
    def update(self, url):
        pfeed = feedparser.parse(url[0])
        initial_update = True
        
        for i in self.menu.get_children():
            if i.get_label() == pfeed.feed.title:
                i.set_submenu(self.build_submenu(pfeed))
                initial_update = False
                break

        if initial_update:
            feed = Gtk.MenuItem()
            feed.set_label(pfeed.feed.title)
            feed.set_submenu(self.build_submenu(pfeed))

            self.menu.append(feed)

        Notify.Notification.new(pfeed.feed.title, str(len(pfeed.entries)) + " new articles", "dialog-information").show()

        self.scheduler.enter(url[1], 1, self.update, argument=(url,))
        
    def right_click_event(self, icon, button, time):
        self.menu.show_all()

        def pos(menu, icon):
            return (Gtk.StatusIcon.position_menu(menu, icon))

        self.menu.popup(None, None, pos, self.statusicon, button, time) 
        
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
    aStatusIcon([('http://www.osnews.com/files/recent.xml', 86400), ('http://feeds.arstechnica.com/arstechnica/index?format=xml', 86400)])
    Gtk.main()
