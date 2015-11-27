#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
    Class for the testing suite :
    - get the list of all test files
    - create a copy of them on start
    - remove the copy on end
"""

import shutil
import os
import glob
import sys
import tempfile
import unittest

IS_LOCAL = True

VERBOSITY = 15

clean = glob.glob('clean*')
clean.sort()
dirty = glob.glob('dirty*')
dirty.sort()

FILE_LIST = zip(clean, dirty)

try:  # PDF render processing
    import cairo
    import gi
    from gi.repository import Poppler
    import pdfrw
except ImportError:
    FILE_LIST.remove(('clean é.pdf', 'dirty é.pdf'))

try:  # python-mutagen : audio file format
    import mutagen
except ImportError:
    FILE_LIST.remove(('clean é.ogg', 'dirty é.ogg'))
    FILE_LIST.remove(('clean é.mp3', 'dirty é.mp3'))
    FILE_LIST.remove(('clean é.flac', 'dirty é.flac'))

try:  # exiftool
    subprocess.check_output(['exiftool', '-ver'])
except:
    FILE_LIST.remove(('clean é.tif', 'dirty é.tif'))

class MATTest(unittest.TestCase):
    """
        Parent class of all test-functions
    """

    def setUp(self):
        """
            Create working copy of the clean and the dirty file in the TMP dir
        """
        self.file_list = []
        self.tmpdir = tempfile.mkdtemp()

        for clean_file, dirty_file in FILE_LIST:
            clean_dir = os.path.join(self.tmpdir, clean_file)
            dirty_dir = os.path.join(self.tmpdir, dirty_file)
            shutil.copy2(clean_file, clean_dir)
            shutil.copy2(dirty_file, dirty_dir)
            self.file_list.append((clean_dir, dirty_dir))

    def tearDown(self):
        """
            Remove the tmp folder
        """
        for root, dirs, files in os.walk(self.tmpdir):
            for d in dirs + files:
                os.chmod(os.path.join(root, d), 0o777)
        shutil.rmtree(self.tmpdir)


def run_all_tests():
    """
    This method will run all tests, both for cli and lib.
    The imports of clitest and libtest are done here because
    of dependencie on the IS_LOCAL variable.

    If set to true, the tests will be done on the _local_ instance
    of MAT, else, on the _system-wide_ one.
    """
    import clitest
    import libtest
    SUITE = unittest.TestSuite()
    SUITE.addTests(clitest.get_tests())
    SUITE.addTests(libtest.get_tests())

    return unittest.TextTestRunner(verbosity=VERBOSITY).run(SUITE).wasSuccessful()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='MAT testsuite')
    parser.add_argument('-s', '--system', action='store_true',
            help='Test the system-wide version of mat')

    if parser.parse_args().system is True:
        IS_LOCAL = False

    sys.exit(run_all_tests() is False)
