""" Care about office's formats

"""

import logging
import os
import shutil
import tempfile
import xml.dom.minidom as minidom
import zipfile

try:
    import cairo
    import gi
    gi.require_version('Poppler', '0.18')
    from gi.repository import Poppler
except ImportError:
    logging.info('office.py loaded without PDF support')

from libmat import parser
#from libmat import archive


class PdfStripper(parser.GenericParser):
    """ Represent a PDF file
    """

    def __init__(self, filename, mime, backup, is_writable, **kwargs):
        super(PdfStripper, self).__init__(filename, mime, backup, is_writable, **kwargs)
        self.uri = 'file://' + os.path.abspath(self.filename)
        self.password = None
        try:
            self.pdf_quality = kwargs['low_pdf_quality']
        except KeyError:
            self.pdf_quality = False

        self.meta_list = frozenset(['title', 'author', 'subject',
                                    'keywords', 'creator', 'producer', 'metadata'])

    def is_clean(self):
        """ Check if the file is clean from harmful metadatas
        """
        document = Poppler.Document.new_from_file(self.uri, self.password)
        return not any(document.get_property(key) for key in self.meta_list)

    def remove_all(self):
        """ Opening the PDF with poppler, then doing a render
            on a cairo pdfsurface for each pages.

            http://cairographics.org/documentation/pycairo/2/

            The use of an intermediate tempfile is necessary because
            python-cairo segfaults on unicode.
            See http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=699457
        """
        document = Poppler.Document.new_from_file(self.uri, self.password)
        try:
            output = tempfile.mkstemp()[1]

            # Size doesn't matter (pun intended),
            # since the surface will be resized before
            # being rendered
            surface = cairo.PDFSurface(output, 10, 10)
            context = cairo.Context(surface)  # context draws on the surface

            logging.debug('PDF rendering of %s', self.filename)
            for pagenum in range(document.get_n_pages()):
                page = document.get_page(pagenum)
                page_width, page_height = page.get_size()
                surface.set_size(page_width, page_height)
                context.save()
                if self.pdf_quality:  # this may reduce the produced PDF size
                    page.render(context)
                else:
                    page.render_for_printing(context)
                context.restore()
                context.show_page()  # draw context on surface
            surface.finish()
            shutil.move(output, self.output)
        except:
            logging.error('Something went wrong when cleaning %s.', self.filename)
            return False

        try:
            # For now, cairo cannot write meta, so we must use pdfrw
            # See the realted thread: http://lists.cairographics.org/archives/cairo/2007-September/011466.html
            import pdfrw

            logging.debug('Removing %s\'s superficial metadata', self.filename)
            trailer = pdfrw.PdfReader(self.output)
            trailer.Info.Producer = None
            trailer.Info.Creator = None
            writer = pdfrw.PdfWriter()
            writer.trailer = trailer
            writer.write(self.output)
            self.do_backup()
        except:
            logging.error('Unable to remove all metadata from %s, please install pdfrw', self.output)
            return False
        return True

    def get_meta(self):
        """ Return a dict with all the meta of the file
        """
        document = Poppler.Document.new_from_file(self.uri, self.password)
        metadata = {}
        for key in self.meta_list:
            if document.get_property(key):
                metadata[key] = document.get_property(key)
        return metadata
