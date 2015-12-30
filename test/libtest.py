#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
    Unit test for the library
"""

import os
import sys
import stat
import shutil
import tarfile
import tempfile
import unittest

import test
import libmat


class TestRemovelib(test.MATTest):
    """ test the remove_all() method
    """

    def test_remove(self):
        """make sure that the lib remove all compromizing meta"""
        for _, dirty in self.file_list:
            current_file = libmat.mat.create_class_file(dirty, False, add2archive=True)
            current_file.remove_all()
            current_file = libmat.mat.create_class_file(dirty, False, add2archive=True)
            self.assertTrue(current_file.is_clean())

    def test_remove_fileformat_specific_options(self):
        """ test metadata removal with fileformat-specific options """
        for _, dirty in self.file_list:  # can't be faster than that :/
            if dirty.endswith('pdf'):
                current_file = libmat.mat.create_class_file(dirty, False, add2archive=True, low_pdf_quality=True)
                current_file.remove_all()
                current_file = libmat.mat.create_class_file(dirty, False, add2archive=True, low_pdf_quality=True)
                self.assertTrue(current_file.is_clean())

    def test_remove_empty(self):
        """Test removal with clean files"""
        for clean, _ in self.file_list:
            current_file = libmat.mat.create_class_file(clean, False, add2archive=True)
            current_file.remove_all()
            current_file = libmat.mat.create_class_file(clean, False, add2archive=True)
            self.assertTrue(current_file.is_clean())


class TestListlib(test.MATTest):
    """ test the get_meta() method
    """

    def test_list(self):
        """check if get_meta returns metadata"""
        for _, dirty in self.file_list:
            current_file = libmat.mat.create_class_file(dirty, False, add2archive=True)
            self.assertIsNotNone(current_file.get_meta())

    def testlist_list_empty(self):
        """check that a listing of a clean file returns an empty dict"""
        for clean, _ in self.file_list:
            current_file = libmat.mat.create_class_file(clean, False, add2archive=True)
            self.assertEqual(current_file.get_meta(), dict())


class TestisCleanlib(test.MATTest):
    """ Test the is_clean() method
    """

    def test_dirty(self):
        """test is_clean on dirty files"""
        for _, dirty in self.file_list:
            current_file = libmat.mat.create_class_file(dirty, False, add2archive=True)
            self.assertFalse(current_file.is_clean())

    def test_clean(self):
        """test is_clean on clean files"""
        for clean, _ in self.file_list:
            current_file = libmat.mat.create_class_file(clean, False, add2archive=True)
            self.assertTrue(current_file.is_clean())


class TestFileAttributes(unittest.TestCase):
    """
        test various stuffs about files (readable, writable, exist, ...)
    """

    def test_not_exist(self):
        """ test MAT's behaviour on non-existent file"""
        self.assertFalse(libmat.mat.create_class_file('non_existent_file', False, add2archive=True))

    def test_empty(self):
        """ test MAT's behaviour on empty file"""
        open('empty_file', 'a').close()
        self.assertFalse(libmat.mat.create_class_file('empty_file', False, add2archive=True))
        os.remove('empty_file')

    def test_not_writtable(self):
        """ test MAT's behaviour on non-writable file"""
        self.assertFalse(libmat.mat.create_class_file('not_writtable', False, add2archive=True))

    def test_not_readable(self):
        """ test MAT's behaviour on non-readable file"""
        open('non_readable', 'a').close()
        os.chmod('non_readable', 0 | stat.S_IWRITE)
        self.assertFalse(libmat.mat.create_class_file('non_readable', False, add2archive=True))
        os.remove('non_readable')


class TestSecureRemove(unittest.TestCase):
    """ Test the secure_remove function
    """

    def test_remove_existing(self):
        """ test the secure removal of an existing file
        """
        _, file_to_remove = tempfile.mkstemp()
        self.assertTrue(libmat.mat.secure_remove(file_to_remove))

    def test_remove_fail(self):
        """ test the secure removal of an non-removable file
        """
        self.assertRaises(libmat.exceptions.UnableToWriteFile, libmat.mat.secure_remove, '/NOTREMOVABLE')


class TestArchiveProcessing(test.MATTest):
    """ Test archives processing
    """

    def test_remove_bz2(self):
        """ Test MAT's ability to process .tar.bz2
        """
        tarpath = os.path.join(self.tmpdir, "test.tar.bz2")
        tar = tarfile.open(tarpath, "w:bz2")
        for clean, dirty in self.file_list:
            tar.add(dirty)
            tar.add(clean)
        tar.close()
        current_file = libmat.mat.create_class_file(tarpath, False, add2archive=False)
        current_file.remove_all()
        current_file = libmat.mat.create_class_file(tarpath, False, add2archive=False)
        self.assertTrue(current_file.is_clean())

    def test_remove_tar(self):
        """ Test MAT on tar files
        """
        tarpath = os.path.join(self.tmpdir, "test.tar")
        tar = tarfile.open(tarpath, "w")
        for clean, dirty in self.file_list:
            tar.add(dirty)
            tar.add(clean)
        tar.close()
        current_file = libmat.mat.create_class_file(tarpath, False, add2archive=False)
        current_file.remove_all()
        current_file = libmat.mat.create_class_file(tarpath, False, add2archive=False)
        self.assertTrue(current_file.is_clean())

    def test_remove_gz(self):
        """ Test MAT on tar.gz files
        """
        tarpath = os.path.join(self.tmpdir, "test.tar.gz")
        tar = tarfile.open(tarpath, "w")
        for clean, dirty in self.file_list:
            tar.add(dirty)
            tar.add(clean)
        tar.close()
        current_file = libmat.mat.create_class_file(tarpath, False, add2archive=False)
        current_file.remove_all()
        current_file = libmat.mat.create_class_file(tarpath, False, add2archive=False)
        self.assertTrue(current_file.is_clean())

    def test_get_unsupported(self):
        """ Test the get_unsupported feature, used by the GUI
        """
        tarpath = os.path.join(self.tmpdir, "test.tar.bz2")
        tar = tarfile.open(tarpath, "w")
        for f in ('libtest.py', 'test.py', 'clitest.py'):
            tar.add(f, f)
        tar.close()
        current_file = libmat.mat.create_class_file(tarpath, False, add2archive=False)
        unsupported_files = set(current_file.is_clean(list_unsupported=True))
        self.assertEqual(unsupported_files, {'libtest.py', 'test.py', 'clitest.py'})

    def test_archive_unwritable_content(self):
        path = os.path.join(self.tmpdir, './unwritable_content.zip')
        shutil.copy2('./unwritable_content.zip', self.tmpdir)
        current_file = libmat.mat.create_class_file(path, False, add2archive=False)
        current_file.remove_all()
        current_file = libmat.mat.create_class_file(path, False, add2archive=False)
        self.assertTrue(current_file.is_clean())


def get_tests():
    """ Returns every libtests"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRemovelib))
    suite.addTest(unittest.makeSuite(TestListlib))
    suite.addTest(unittest.makeSuite(TestisCleanlib))
    suite.addTest(unittest.makeSuite(TestFileAttributes))
    suite.addTest(unittest.makeSuite(TestSecureRemove))
    suite.addTest(unittest.makeSuite(TestArchiveProcessing))
    return suite
