""" Care about images with help of the amazing (perl) library Exiftool.
"""

import subprocess
from libmat import parser


class ExiftoolStripper(parser.GenericParser):
    """ A generic stripper class using exiftool as backend
    """

    def __init__(self, filename, mime, backup, is_writable, **kwargs):
        super(ExiftoolStripper, self).__init__(filename, mime, backup, is_writable, **kwargs)
        self.allowed = {'ExifTool Version Number', 'File Name', 'Directory', 'File Size', 'File Modification Date/Time',
                        'File Access Date/Time', 'File Permissions', 'File Type', 'File Type Extension', 'MIME Type',
                        'Image Width', 'Image Height', 'Image Size', 'File Inode Change Date/Time', 'Megapixels'}
        self._set_allowed()

    def _set_allowed(self):
        """ Virtual method. Set the allowed/harmless list of metadata
        """
        raise NotImplementedError

    def remove_all(self):
        """ Remove all metadata with help of exiftool
        """
        try:
            if self.backup:
                self.create_backup_copy()
            # Note: '-All=' must be followed by a known exiftool option.
            # Also, '-CommonIFD0' is needed for .tiff files
            subprocess.call(['exiftool', '-all=', '-adobe=', '-exif:all=', '-Time:All=', '-m',
                             '-CommonIFD0=', '-overwrite_original', self.filename],
                            stdout=open('/dev/null'), stderr=open('/dev/null'))
            return True
        except OSError:
            return False

    def is_clean(self):
        """ Check if the file is clean with the help of exiftool
        """
        return not self.get_meta()

    def get_meta(self):
        """ Return every harmful meta with help of exiftool.
            Exiftool output looks like this:
            field name : value
            field name : value
        """
        output = subprocess.Popen(['exiftool', self.filename],
                                  stdout=subprocess.PIPE).communicate()[0]
        meta = {}
        for i in output.split('\n')[:-1]:  # chop last char ('\n')
            key = i.split(':')[0].strip()
            if key not in self.allowed:
                meta[key] = i.split(':')[1].strip()  # add the field name to the metadata set
        return meta


class JpegStripper(ExiftoolStripper):
    """ Care about jpeg files with help
        of exiftool
    """

    def _set_allowed(self):
        self.allowed.update(['JFIF Version', 'Resolution Unit',
                             'X Resolution', 'Y Resolution', 'Encoding Process',
                             'Bits Per Sample', 'Color Components', 'Y Cb Cr Sub Sampling'])


class PngStripper(ExiftoolStripper):
    """ Care about png files with help
        of exiftool
    """

    def _set_allowed(self):
        self.allowed.update(['Bit Depth', 'Color Type',
                             'Compression', 'Filter', 'Interlace', 'Palette',
                             'Pixels Per Unit X',
                             'Pixels Per Unit Y', 'Pixel Units', 'Significant Bits',
                             'Background Color', 'SRGB Rendering'])


class TiffStripper(ExiftoolStripper):
    """ Care about tiff files with help
        of exiftool
    """

    def _set_allowed(self):
        # Todo: it would be awesome to detect the Resolution Unit, and to transform it in centimeter if it's in inches.
        self.allowed.update(['X Resolution', 'Y Resolution', 'Compression', 'Bits Per Sample',
                             'Strip Offsets', 'Photometric Interpretation', 'Strip Byte Counts',
                             'Resolution Unit', 'Exif Byte Order', 'Samples Per Pixel', 'Rows Per Strip',
                             'Orientation'])
