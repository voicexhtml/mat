'''
    Care about office's formats
'''

import os
import mimetypes
import subprocess
import tempfile
import glob
import logging
import zipfile
import re
import shutil
from xml.etree import ElementTree

try:
    import cairo
    import poppler
except ImportError:
    pass

import mat
import parser
import archive
import pdfrw


class OpenDocumentStripper(archive.GenericArchiveStripper):
    '''
        An open document file is a zip, with xml file into.
        The one that interest us is meta.xml
    '''

    def get_meta(self):
        '''
            Return a dict with all the meta of the file
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        metadata = {}
        try:
            content = zipin.read('meta.xml')
            zipin.close()
            tree = ElementTree.fromstring(content)
            for node in tree.iter():
                key = re.sub('{.*}', '', node.tag)
                metadata[key] = node.text
        except KeyError:  # no meta.xml file found
            logging.debug('%s has no opendocument metadata' % self.filename)
        return metadata

    def _remove_all(self, method):
        '''
            FIXME ?
            There is a patch implementing the Zipfile.remove()
            method here : http://bugs.python.org/issue6818
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        zipout = zipfile.ZipFile(self.output, 'w',
            allowZip64=True)
        for item in zipin.namelist():
            name = os.path.join(self.tempdir, item)
            if item.endswith('.xml') or item == 'mimetype':
                #keep .xml files, and the "manifest" file
                if item != 'meta.xml':  # contains the metadata
                    zipin.extract(item, self.tempdir)
                    zipout.write(name, item)
                    mat.secure_remove(name)
            elif item.endswith('manifest.xml'):
                zipin.extract(item, self.tempdir)
                #remove line meta.xml
                zipout.write(name, item)
                mat.secure_remove(name)
            else:
                zipin.extract(item, self.tempdir)
                if os.path.isfile(name):
                    try:
                        cfile = mat.create_class_file(name, False,
                            self.add2archive)
                        if method == 'normal':
                            cfile.remove_all()
                        else:
                            cfile.remove_all_ugly()
                        logging.debug('Processing %s from %s' % (item,
                            self.filename))
                        zipout.write(name, item)
                    except:
                        logging.info('%s\' fileformat is not supported' % item)
                        if self.add2archive:
                            zipout.write(name, item)
                    mat.secure_remove(name)
        zipout.comment = ''
        logging.info('%s treated' % self.filename)
        zipin.close()
        zipout.close()
        self.do_backup()

    def is_clean(self):
        '''
            Check if the file is clean from harmful metadatas
        '''
        zipin = zipfile.ZipFile(self.filename, 'r')
        try:
            zipin.getinfo('meta.xml')
            return False
        except KeyError:  # no meta.xml in the file
                zipin.close()
                czf = archive.ZipStripper(self.filename, self.parser,
                    'application/zip', self.backup, self.add2archive)
                if czf.is_clean():
                    return True
                else:
                    return False
        return True


class PdfStripper(parser.GenericParser):
    '''
        Represent a pdf file
    '''
    def __init__(self, filename, parser, mime, backup, add2archive):
        super(PdfStripper, self).__init__(filename, parser, mime, backup,
            add2archive)
        uri = 'file://' + self.filename
        self.password = None
        self.document = poppler.document_new_from_file(uri, self.password)
        self.meta_list = ('title', 'author', 'subject', 'keywords', 'creator',
            'producer', 'creation-date', 'mod-date', 'metadata')

    def is_clean(self):
        '''
            Check if the file is clean from harmful metadatas
        '''
        for key in self.meta_list:
            if key == 'creation-date' and key == 'mod-date':
                if self.document.get_property(key) != -1:
                    return False
            else:
                if self.document.get_property(key) is not None:
                    return False
        return True

    def remove_all(self):
        '''
            Opening the pdf with poppler, then doing a render
            on a cairo pdfsurface for each pages.
            http://cairographics.org/documentation/pycairo/2/
            python-poppler is not documented at all : have fun ;)
        '''
        page = self.document.get_page(0)
        page_width, page_height = page.get_size()
        surface = cairo.PDFSurface(self.output, page_width, page_height)
        context = cairo.Context(surface) #  context draws on the surface
        for pagenum in xrange(self.document.get_n_pages()):
            page = self.document.get_page(pagenum)
            context.translate(0, 0)
            page.render(context) #  render the page on context
            context.show_page() #  draw context on surface
        surface.finish()

        #For now, poppler cannot write meta, so we must use pdfrw
        trailer = pdfrw.PdfReader(self.output)
        trailer.Info.Producer = trailer.Info.Creator = None
        writer = pdfrw.PdfWriter()
        writer.trailer = trailer
        writer.write(self.output)
        self.do_backup()

    def get_meta(self):
        '''
            Return a dict with all the meta of the file
        '''
        metadata={}
        for key in self.meta_list:
            if key == 'creation-date' or key == 'mod-date':
                #creation and modification are set to -1
                if self.document.get_property(key) != -1:
                    metadata[key] = self.document.get_property(key)
            else:
                if self.document.get_property(key) is not None and \
                    self.document.get_property(key) != '':
                        metadata[key] = self.document.get_property(key)
        return metadata