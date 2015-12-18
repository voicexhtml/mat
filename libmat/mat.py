#!/usr/bin/env python

""" Metadata anonymisation toolkit library
"""

import logging
import mimetypes
import os
import platform
import subprocess
import xml.sax

import libmat.exceptions

__version__ = '0.5.4'
__author__ = 'jvoisin'

# Silence
LOGGING_LEVEL = logging.ERROR
fname = ''

# Verbose
# LOGGING_LEVEL = logging.DEBUG
# logname = 'report.log'

logging.basicConfig(filename=fname, level=LOGGING_LEVEL)

import strippers  # this is loaded here because we need LOGGING_LEVEL


def get_logo():  # pragma: no cover
    """ Return the path to the logo
    """
    if os.path.isfile(os.path.join(os.path.curdir, 'data/mat.png')):
        return os.path.join(os.path.curdir, 'data/mat.png')
    elif os.path.isfile('/usr/share/pixmaps/mat.png'):
        return '/usr/share/pixmaps/mat.png'
    elif os.path.isfile('/usr/local/share/pixmaps/mat.png'):
        return '/usr/local/share/pixmaps/mat.png'


def get_datafile_path(filename):  # pragma: no cover
    """ Return the path to $filename
    :param string filename:
    """
    paths = ['data', '/usr/local/share/mat/', '/usr/share/mat/']
    for path in paths:
        filepath = os.path.join(os.path.curdir, path, filename)
        if os.path.isfile(filepath):
            return filepath


def list_supported_formats():  # pragma: no cover
    """ Return a list of all locally supported fileformat.
        It parses that FORMATS file, and removes locally
        non-supported formats.
    """
    handler = XMLParser()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    path = get_datafile_path('FORMATS')
    with open(path, 'r') as xmlfile:
        parser.parse(xmlfile)

    localy_supported = []
    for item in handler.list:
        if item['mimetype'].split(',')[0] in strippers.STRIPPERS:
            localy_supported.append(item)

    return localy_supported


class XMLParser(xml.sax.handler.ContentHandler):  # pragma: no cover
    """ Parse the supported format xml, and return a corresponding
        list of dict
    """

    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self.dict = {}
        self.list = []
        self.content, self.key = '', ''
        self.between = False

    def startElement(self, name, attrs):
        """ Called when entering into xml tag
        """
        self.between = True
        self.key = name
        self.content = ''

    def endElement(self, name):
        """ Called when exiting a xml tag
        """
        if name == 'format':  # leaving a fileformat section
            self.list.append(self.dict.copy())
            self.dict.clear()
        else:
            content = self.content.replace('\s', ' ')
            self.dict[self.key] = content
            self.between = False

    def characters(self, characters):
        """ Concatenate the content between opening and closing tags
        """
        if self.between:
            self.content += characters


def secure_remove(filename):
    """ Securely remove $filename
    :param str filename: File to be removed
    """
    try:  # I want the file removed, even if it's read-only
        os.chmod(filename, 220)
    except OSError:
        logging.error('Unable to add write rights to %s', filename)
        raise libmat.exceptions.UnableToWriteFile

    try:
        shred = 'shred'
        if platform.system() == 'MacOS':
            shred = 'gshred'
        if not subprocess.call([shred, '--remove', filename]):
            return True
        else:
            raise OSError
    except OSError:
        logging.error('Unable to securely remove %s', filename)

    try:
        os.remove(filename)
    except OSError:
        logging.error('Unable to remove %s', filename)
        raise libmat.exceptions.UnableToRemoveFile

    return True


def create_class_file(name, backup, **kwargs):
    """ Return a $FILETYPEStripper() class,
        corresponding to the filetype of the given file

        :param str name: name of the file to be parsed
        :param bool backup: shell the file be backuped?
    """
    if not os.path.isfile(name):  # check if the file exists
        logging.error('%s is not a valid file', name)
        return None
    elif not os.access(name, os.R_OK):  # check read permissions
        logging.error('%s is is not readable', name)
        return None

    mime = mimetypes.guess_type(name)[0]
    if not mime:
        logging.info('Unable to find mimetype of %s', name)
        return None

    if mime.startswith('application/vnd.oasis.opendocument'):
        mime = 'application/opendocument'  # opendocument fileformat
    elif mime.startswith('application/vnd.openxmlformats-officedocument'):
        mime = 'application/officeopenxml'  # office openxml

    is_writable = os.access(name, os.W_OK)

    try:
        stripper_class = strippers.STRIPPERS[mime]
    except KeyError:
        logging.info('Don\'t have stripper for %s format', mime)
        return None

    return stripper_class(name, mime, backup, is_writable, **kwargs)
