#! /usr/bin/python

import os
import urllib
import logging
import gettext
gettext.install('mat')

import xml.sax
import nautilus
import gtk

# mat package is called lib
from MAT import mat, strippers

class MatExtension(nautilus.MenuProvider):
    def __init__(self):
        logging.debug('nautilus-mat: initializing')
        pass

    def get_file_items(self, window, files):
        if len(files) != 1:
            return

        file = files[0]

        # We're only going to put ourselves on supported mimetypes' context menus
        if not file.get_mime_type() in [i['mimetype'] for i in self.__list_supported()]:
            logging.debug('%s is not supported by MAT' % file.get_mime_type())
            return

        # MAT can only handle local file:
        if file.get_uri_scheme() != 'file':
            ligging.debug('%s files not supported by MAT' % file.get_uri_scheme())
            return

        item = nautilus.MenuItem(name='Nautilus::clean_metadata',
                                 label=_('Clean metadata'),
                                 tip=_('Clean file\'s metadata with MAT'))
        item.connect('activate', self.menu_activate_cb, file)
        return item,

    def show_message(self, message, type = gtk.MESSAGE_INFO):
        dialog = gtk.MessageDialog(parent=None,
                                   flags=gtk.DIALOG_MODAL,
                                   type=type,
                                   buttons=gtk.BUTTONS_OK,
                                   message_format=message)
        ret = dialog.run()
        dialog.destroy()
        return ret

    # Convenience functions that should be merged into MAT core
    def __list_supported(self):
        '''
            Print all supported fileformat, and exit
        '''
        handler = mat.XMLParser()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        path = os.path.join(mat.get_sharedir('FORMATS'))
        with open(path, 'r') as xmlfile:
            parser.parse(xmlfile)

        localy_supported = []
        for item in handler.list:
            if strippers.STRIPPERS.has_key(item['mimetype'].split(',')[0]):
                localy_supported.append(item)

        return localy_supported

    def menu_activate_cb(self, menu, file):
        if file.is_gone():
            return

        file_path = urllib.unquote(file.get_uri()[7:])

        class_file = mat.create_class_file(file_path,
                                           backup=True,
                                           add2archive=False)
        if class_file:
            if class_file.is_clean():
                self.show_message(_('%s is already clean') % file_path)
            else:
                if not class_file.remove_all():
                    self.show_message(_('Unable to clean %s') % file_path, gtk.MessageType.ERROR)
        else:
            self.show_message(_('Unable to process %s') % file_path, gtk.MessageType.ERROR)


