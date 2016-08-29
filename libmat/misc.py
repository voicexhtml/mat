""" Care about misc formats
"""

from libmat import parser

from libmat.bencode import bencode


class TorrentStripper(parser.GenericParser):
    """ Represent a torrent file with the help
        of the bencode lib from Petru Paler
    """

    def __init__(self, filename, mime, backup, is_writable, **kwargs):
        super(TorrentStripper, self).__init__(filename, mime, backup, is_writable, **kwargs)
        self.fields = frozenset(['announce', 'info', 'name', 'path', 'piece length', 'pieces',
                                 'length', 'files', 'announce-list', 'nodes', 'httpseeds', 'private', 'root hash'])

    def __get_key_recursively(self, dictionary):
        """ Get recursively all keys from a dict and
            its subdicts
        """
        for i, j in list(dictionary.items()):
            if isinstance(j, dict):
                return {i}.union(self.__get_key_recursively(j))
            return {i}

    def is_clean(self):
        """ Check if the file is clean from harmful metadata
        """
        with open(self.filename, 'r') as f:
            decoded = bencode.bdecode(f.read())
        return self.fields.issuperset(self.__get_key_recursively(decoded))

    def __get_meta_recursively(self, dictionary):
        """ Get recursively all harmful metadata
        """
        d = dict()
        for i, j in list(dictionary.items()):
            if i not in self.fields:
                d[i] = j
            elif isinstance(j, dict):
                d = dict(d.items() + list(self.__get_meta_recursively(j).items()))
        return d

    def get_meta(self):
        """ Return a dict with all the meta of the file
        """
        with open(self.filename, 'r') as f:
            decoded = bencode.bdecode(f.read())
        return self.__get_meta_recursively(decoded)

    def __remove_all_recursively(self, dictionary):
        """ Remove recursively all compromizing fields
        """
        d = dict()
        for i, j in list(dictionary.items()):
            if i not in self.fields:
                continue
            elif isinstance(j, dict):
                d = dict(list(d.items()) + list(self.__get_meta_recursively(j).items()))
            else:
                d[i] = j
        return d

    def remove_all(self):
        """ Remove all comprimizing fields
        """
        with open(self.filename, 'rb') as f:
            decoded = bencode.bdecode(f.read())

        cleaned = self.__remove_all_recursively(decoded)

        with open(self.output, 'w') as f:  # encode the decoded torrent
            f.write(bencode.bencode(cleaned))  # and write it in self.output

        self.do_backup()
        return True
