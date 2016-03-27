""" Take care of mutagen-supported formats (audio)
"""

from libmat import parser

import mutagen
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.mp3 import MP3


class MutagenStripper(parser.GenericParser):
    """ Parser using the (awesome) mutagen library. """
    def __init__(self, filename, mime, backup, is_writable, **kwargs):
        super(MutagenStripper, self).__init__(filename, mime, backup, is_writable, **kwargs)
        self.mfile = None  # This will be instanciated in self._create_mfile()
        self._create_mfile()

    def _create_mfile(self):
        """ This method must be overridden to instantiate the `mfile` attribute."""
        raise NotImplementedError

    def is_clean(self):
        """ Check if the file is clean. """
        return not self.mfile.tags

    def remove_all(self):
        """ Remove all harmful metadata. """
        if self.backup:
            self.create_backup_copy()
        self.mfile.delete()
        try:  # mutagen will choke on files without a metadata block
            self.mfile.save()
        except ValueError:
            pass
        return True

    def get_meta(self):
        """
            Return the content of the metadata block is present
        """
        metadata = {}
        if self.mfile.tags:
            for key, value in self.mfile.tags:
                metadata[key] = value
        return metadata


class MpegAudioStripper(MutagenStripper):
    """ Represent a mp3 vorbis file
    """
    def _create_mfile(self):
        self.mfile = MP3(self.filename)

    def get_meta(self):
        """
            Return the content of the metadata block is present
        """
        metadata = {}
        if self.mfile.tags:
            for key in self.mfile.tags.keys():
                meta = self.mfile.tags[key]
                try:  # Sometimes, the field has a human-redable description
                    desc = meta.desc
                except AttributeError:
                    desc = key
                text = meta.text[0]
                metadata[desc] = text
        return metadata


class OggStripper(MutagenStripper):
    """ Represent an ogg vorbis file
    """
    def _create_mfile(self):
        self.mfile = OggVorbis(self.filename)


class FlacStripper(MutagenStripper):
    """ Represent a Flac audio file
    """
    def _create_mfile(self):
        self.mfile = FLAC(self.filename)

    def remove_all(self):
        """ Remove the "metadata" block from the file
        """
        super(FlacStripper, self).remove_all()
        self.mfile.clear_pictures()
        self.mfile.save()
        return True

    def is_clean(self):
        """ Check if the "metadata" block is present in the file
        """
        return super(FlacStripper, self).is_clean() and not self.mfile.pictures

    def get_meta(self):
        """ Return the content of the metadata block if present
        """
        metadata = super(FlacStripper, self).get_meta()
        if self.mfile.pictures:
            metadata['picture:'] = 'yes'
        return metadata
