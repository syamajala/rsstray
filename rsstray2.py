#!/usr/bin/python
from gi.repository import Gtk, GObject, Gdk
from gi.repository import Notify
import feedparser
import webbrowser
import threading
import sched
import time
import shelve
import os


class Article():

    def __init__(self, url, feed, title, read=False):
        self.url = url
        self.feed = feed
        self.title = title
        self.read = read
        self.label = None

        self.label = Gtk.MenuItem()
        self.label.set_label(self.title)
        self.label.connect("activate", lambda x: webbrowser.open(self.url))


class Feed():

    def __init__(self, url, refreshrate=86400):
        self.url = url
        self.refreshrate = refreshrate
        self.name = None
        self.articles = []
        self.menu = None
        self.icon = None

        self.update()

    def update(self):
        self.pfeed = feedparser.parse(self.url)

        if self.pfeed.bozo:
            print("Feed Error!!!")

        self.name = self.pfeed.feed.title
        if not self.articles:
            self.articles = [Article(i.link, self, i.title, False)
                             for i in self.pfeed.entries]

            self.menu = Gtk.Menu()
            for i in self.articles:
                self.menu.append(i.label)


class Handlers():

    def add(self, button):
        feedwindow.show_all()

    def remove(self):
        pass

    def edit(self, button):
        pass

    def feed_ok(self, button):
        url = builder.get_object('url')
        refreshrate = builder.get_object('refreshrate')
        new_feed = Feed(url.get_text(), int(refreshrate.get_text()))
        feeds['url'] = new_feed
        feedlist.append([new_feed.url])

        feedwindow.destroy()

    def feed_cancel(self, button):
        feedwindow.destroy()

    def config_ok(self, button):
        config_window.destroy()

    def config_cancel(self, button):
        config_window.destroy()

    def feedlistview_selection(self, selection):
        pass

    def tray_right_click(self, icon, button, ctime):
        tray_menu.show_all()

        def pos(menu, icon):
            return (Gtk.StatusIcon.position_menu(menu, icon))

        tray_menu.popup(None, None, pos, builder.get_object('rsstray'),
                        button, ctime)

    def tray_quit(self, args):
        config.close()
        Gtk.main_quit()


if __name__ == '__main__':

    GObject.threads_init()
    Gdk.threads_init()
    Notify.init('RSS Tray')
    Gtk.init()

    cache_path = os.path.expanduser("~/.cache") + '/rsstray'

    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    config_path = os.path.expanduser("~/.config") + '/rsstray'

    if not os.path.exists(config_path):
        os.makedirs(config_path)

    config_file = config_path + '/rsstray.conf'
    config = shelve.open(config_file)

    builder = Gtk.Builder()
    builder.add_from_file("rsstray.glade")
    builder.connect_signals(Handlers())
    config_window = builder.get_object("configurationwindow")
    feedwindow = builder.get_object("feedwindow")

    feedlist = Gtk.ListStore(str)
    feedlistview = builder.get_object("feedlistview")
    feedlistview.set_model(feedlist)

    renderer = Gtk.CellRendererText()
    feedcolumn = Gtk.TreeViewColumn("Name", renderer, text=0)
    feedlistview.append_column(feedcolumn)

    feeds = {}
    tray_menu = builder.get_object("tray_menu")

    try:
        feeds = config['feeds']
        for i in feeds:
            i.update()
    except KeyError:
        config_window.show_all()
        NoFeeds = Gtk.MessageDialog(config_window, Gtk.DialogFlags.MODAL,
                                    Gtk.MessageType.ERROR,
                                    Gtk.ButtonsType.OK,
                                    "Please add feeds.")
        NoFeeds.run()
        NoFeeds.destroy()

    Gtk.main()
