#! /usr/bin/python

""" This file is an extension for the Nautilus
    file manager, to provide a contextual menu to
    clean metadata
"""

import logging
import urllib

try:
    import gettext

    gettext.install("mat")
except:
    logging.warning("Failed to initialise gettext")
    _ = lambda x: x

from gi.repository import Nautilus, GObject, Gtk

import libmat.mat
import libmat.strippers


class MatExtension(GObject.GObject, Nautilus.MenuProvider):
    """ A nautilus extension, acting as a frontend to MAT, to clean metadata."""

    def __init__(self):
        logging.debug("nautilus-mat: initialising")

    def get_file_items(self, window, files):
        if len(files) != 1:  # no multi-files support
            return

        current_file = files.pop()

        # We're only going to put ourselves on supported mimetypes' context menus
        if not (current_file.get_mime_type()
                in [i["mimetype"] for i in libmat.mat.list_supported_formats()]):
            logging.debug("%s is not supported by MAT", current_file.get_mime_type())
            return

        # MAT can only handle local file:
        if current_file.get_uri_scheme() != 'file':
            logging.debug("%s files not supported by MAT", current_file.get_uri_scheme())
            return

        # MAT can not clean non-writable files
        if not current_file.can_write():
            logging.debug("%s is not writable by MAT", current_file.get_uri_scheme())
            return

        item = Nautilus.MenuItem(name="Nautilus::clean_metadata",
                                 label=_("Clean metadata"),
                                 tip=_("Clean file's metadata with MAT"),
                                 icon="gtk-clear")
        item.connect('activate', self.menu_activate_cb, current_file)
        return item,

    @staticmethod
    def show_message(message, msg_type=Gtk.MessageType.INFO):
        """ Helper function to show a message in a popup
        :param msg_type: Type of the message to display
        :param message: Message to display
        """
        dialog = Gtk.MessageDialog(parent=None,
                                   flags=Gtk.DialogFlags.MODAL,
                                   type=msg_type,
                                   buttons=Gtk.ButtonsType.OK,
                                   message_format=message)
        ret = dialog.run()
        dialog.destroy()
        return ret

    def menu_activate_cb(self, menu, current_file):
        """ Callback function, used to clean the file
        :param current_file: Name of the selected file
        :param menu: Menu id from which the callback was activated. Unused.
        """
        if file.is_gone():
            return

        # files url in nautilus are starting with 'file://', of length 7
        file_path = urllib.unquote(current_file.get_uri()[7:])

        class_file = libmat.mat.create_class_file(file_path,
                                                  backup=True,
                                                  add2archive=False)
        if class_file:
            if class_file.is_clean():
                self.show_message(_("%s is already clean") % file_path)
            elif not class_file.remove_all():
                self.show_message(_("Unable to clean %s") % file_path, Gtk.MessageType.ERROR)
        else:
            self.show_message(_("Unable to process %s") % file_path, Gtk.MessageType.ERROR)
