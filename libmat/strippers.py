""" Manage which fileformat can be processed
"""

import archive
import mutagenstripper
import logging
import mat
import misc
import office
import subprocess

STRIPPERS = {
    'application/x-tar': archive.TarStripper,
    'application/x-bzip2': archive.Bzip2Stripper,
    'application/x-gzip': archive.GzipStripper,
    'application/zip': archive.ZipStripper,
    'application/x-bittorrent': misc.TorrentStripper,
    'application/torrent': misc.TorrentStripper,
    'application/opendocument': office.OpenDocumentStripper,
    'application/officeopenxml': office.OpenXmlStripper,
}

logging.basicConfig(level=mat.LOGGING_LEVEL)

# PDF support
pdfSupport = True
try:
    import gi
    gi.require_version('Poppler', '0.18')
    from gi.repository import Poppler
except ImportError:
    logging.error('Unable to import Poppler: no PDF support')
    pdfSupport = False

try:
    import cairo
except ImportError:
    logging.error('Unable to import python-cairo: no PDF support')
    pdfSupport = False

try:
    import pdfrw
except ImportError:
    logging.error('Unable to import python-pdfrw: no PDf support')
    pdfSupport = False

if pdfSupport:
    STRIPPERS['application/x-pdf'] = office.PdfStripper
    STRIPPERS['application/pdf'] = office.PdfStripper


# audio format support with mutagen-python
try:
    import mutagen
    STRIPPERS['audio/x-flac'] = mutagenstripper.FlacStripper
    STRIPPERS['audio/flac'] = mutagenstripper.FlacStripper
    STRIPPERS['audio/vorbis'] = mutagenstripper.OggStripper
    STRIPPERS['audio/ogg'] = mutagenstripper.OggStripper
    STRIPPERS['audio/mpeg'] = mutagenstripper.MpegAudioStripper
except ImportError:
    logging.error('Unable to import python-mutagen: limited audio format support')

# exiftool
try:
    subprocess.check_output(['exiftool', '-ver'])
    import exiftool
    STRIPPERS['image/jpeg'] = exiftool.JpegStripper
    STRIPPERS['image/png'] = exiftool.PngStripper
    STRIPPERS['image/tiff'] = exiftool.TiffStripper
except OSError:
    logging.error('Unable to find exiftool: limited images support')
