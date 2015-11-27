""" Take care of mutagen-supported formats (audio)
"""

import parser


class MutagenStripper(parser.GenericParser):
    """ Parser using the (awesome) mutagen library. """
    def __init__(self, filename, parser, mime, backup, is_writable, **kwargs):
        super(MutagenStripper, self).__init__(filename, parser, mime, backup, is_writable, **kwargs)
        self.mfile = None  # This will be instanciated in self._create_mfile()
        self._create_mfile()

    def _create_mfile(self):
        """ This method must be overrriden to instanciate the `mfile` attribute."""
        raise NotImplementedError

    def is_clean(self):
        """ Check if the file is clean. """
        return not self.mfile.tags

    def remove_all(self):
        """ Remove all harmful metadata. """
        if self.backup:
            self.create_backup_copy()
        self.mfile.delete()
        self.mfile.save()
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
