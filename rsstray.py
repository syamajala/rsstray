#!/usr/bin/python
from gi.repository import Gtk, GObject, Gdk
from gi.repository import Notify
import feedparser
import xml
import urllib.request
import webbrowser
import threading
import sched
import time
import shelve
import os


class Article():

    def __init__(self, url, title, read=False):
        self.url = url
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
        self.title = None
        self.articles = []
        self.menu = None
        self.icon = None
        self.label = None

        self.update()

    def update(self):
        menu_lock.acquire()
        try:
            self.pfeed = feedparser.parse(self.url)

            if self.pfeed.bozo:
                print("feedparser bozo detected.")
                raise self.pfeed.bozo_exception

            if not self.title:
                    self.title = self.pfeed.feed.title

            if not self.articles:
                self.articles = [Article(i.link, i.title, False)
                                 for i in self.pfeed.entries]
                Notify.Notification.new(self.title, str(len(self.articles)) +
                                        " new articles.",
                                        "dialog-information").show()
                self.menu = Gtk.Menu()
                for i in self.articles:
                    self.menu.append(i.label)
            else:
                # remove old articles
                nnew = 0

                for i in range(0, len(self.articles)):
                    if self.pfeed.entries[i].link == self.articles[i].url:
                        if not self.articles[i].read:
                            nnew = nnew + 1
                        else:
                            continue
                    else:
                        self.menu.remove(self.articles[i].label)
                        self.articles.pop(i)

                Notify.Notification.new(self.title,
                                        str(nnew) + " new articles.",
                                        "dialog-information").show()

            scheduler.enter(self.refreshrate, 1, self.update)
            if not schedthread.is_alive():
                schedthread.start()

        finally:
            menu_lock.release()


class Handlers():

    def add(self, button):
        feed_window.show_all()

    def remove(self, button):
        pass

    def edit(self, button):
        pass

    def feed_ok(self, button):
        try:
            new_feed = Feed(url.get_text(), int(refreshrate.get_text()))
            feeds[url.get_text()] = new_feed
            feedlist.append([new_feed.title])

            # img = urllib.request.urlopen(new_feed.pfeed.image['href'])
            # new_feed.icon = cache_path + '/' + new_feed.title + \
            #     new_feed.pfeed.image['href'][-4:]
            # with open(new_feed.icon, 'wb+') as icon:
            #     icon.write(img.read())

            menuitem = Gtk.MenuItem(label=new_feed.title)
            menuitem.set_submenu(new_feed.menu)
            new_feed.label = menuitem
            tray_menu.append(new_feed.label)
#            config['feeds'] = feeds

        except xml.sax._exceptions.SAXParseException:
            InvalidFeed = Gtk.MessageDialog(feed_window, Gtk.DialogFlags.MODAL,
                                            Gtk.MessageType.ERROR,
                                            Gtk.ButtonsType.OK,
                                            "Invalid Feed")
            InvalidFeed.run()
            InvalidFeed.destroy()

        finally:
            feed_window.destroy()

    def feed_cancel(self, button):
        feed_window.destroy()

    def config_close(self, button):
        config_window.hide()

    def feedlistview_selection(self, selection):
        pass

    def tray_right_click(self, icon, button, ctime):
        while not menu_lock.acquire(1):
            menu_lock.acquire(1)

        tray_menu.show_all()

        def pos(menu, icon):
            return (Gtk.StatusIcon.position_menu(menu, icon))

        tray_menu.popup(None, None, pos, builder.get_object('rsstray'),
                        button, ctime)

    def tray_deactivate(self, args):
        menu_lock.release()

    def tray_quit(self, args):
        config.close()
        Gtk.main_quit()

    def preferences(self, args):
        config_window.show_all()

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
    config_window = builder.get_object("config_window")
    config_notebook = builder.get_object("config_notebook")
    feed_window = builder.get_object("feed_window")

    feedlist = Gtk.ListStore(str)
    feedlistview = builder.get_object("feedlistview")
    feedlistview.set_model(feedlist)

    feedlistview_selection = feedlistview.get_selection()
    feedlistview_selection.set_mode(Gtk.SelectionMode.SINGLE)

    url = builder.get_object('url')
    refreshrate = builder.get_object('refreshrate')

    renderer = Gtk.CellRendererText()
    feedcolumn = Gtk.TreeViewColumn("Name", renderer, text=0)
    feedlistview.append_column(feedcolumn)

    feeds = {}
    tray_menu = builder.get_object("tray_menu")
    menu_lock = threading.Lock()

    scheduler = sched.scheduler(time.time, time.sleep)
    schedthread = threading.Thread(target=scheduler.run, daemon=True)

    try:
        feeds = config['feeds']

    except KeyError:
        config_window.show_all()
        NoFeeds = Gtk.MessageDialog(config_window, Gtk.DialogFlags.MODAL,
                                    Gtk.MessageType.ERROR,
                                    Gtk.ButtonsType.OK,
                                    "Please add feeds.")
        NoFeeds.run()
        NoFeeds.destroy()

    Gtk.main()
