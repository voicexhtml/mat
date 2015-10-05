#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
    Unit test for the CLI interface
"""

import os
import unittest
import subprocess
import sys
import tarfile

import test
MAT_PATH = 'mat'
if test.IS_LOCAL is True:
    # Are we testing the _local_ version of MAT?
    sys.path.insert(0, '..')
    MAT_PATH = '../mat'
# else it will be in the path

from libmat import mat


class TestRemovecli(test.MATTest):
    """
        test if cli correctly remove metadatas
    """

    def test_remove(self):
        """make sure that the cli remove all compromizing meta"""
        for _, dirty in self.file_list:
            subprocess.call([MAT_PATH, '--add2archive', dirty])
            current_file = mat.create_class_file(dirty, False, add2archive=True, low_pdf_quality=True)
            self.assertTrue(current_file.is_clean())

    def test_remove_empty(self):
        """Test removal with clean files\n"""
        for clean, _ in self.file_list:
            subprocess.call([MAT_PATH, '--add2archive', clean])
            current_file = mat.create_class_file(clean, False, add2archive=True, low_pdf_quality=True)
            self.assertTrue(current_file.is_clean())


class TestListcli(test.MATTest):
    """
        test if cli correctly display metadatas
    """

    def test_list_clean(self):
        """check if get_meta returns meta"""
        for clean, _ in self.file_list:
            proc = subprocess.Popen([MAT_PATH, '-d', clean],
                                    stdout=subprocess.PIPE)
            stdout, _ = proc.communicate()
            self.assertEqual(str(stdout).strip('\n'), "[+] File %s \
:\nNo harmful metadata found" % clean)

    def test_list_dirty(self):
        """check if get_meta returns all the expected meta"""
        for _, dirty in self.file_list:
            proc = subprocess.Popen([MAT_PATH, '-d', dirty],
                                    stdout=subprocess.PIPE)
            stdout, _ = proc.communicate()
            self.assertNotEqual(str(stdout), "[+] File %s :\n No\
harmul metadata found" % dirty)


class TestisCleancli(test.MATTest):
    """
        check if cli correctly check if a file is clean or not
    """

    def test_clean(self):
        """test is_clean on clean files"""
        for clean, _ in self.file_list:
            proc = subprocess.Popen([MAT_PATH, '-c', clean],
                                    stdout=subprocess.PIPE)
            stdout, _ = proc.communicate()
            self.assertEqual(str(stdout).strip('\n'), '[+] %s is clean' % clean)

    def test_dirty(self):
        """test is_clean on dirty files"""
        for _, dirty in self.file_list:
            proc = subprocess.Popen([MAT_PATH, '-c', dirty],
                                    stdout=subprocess.PIPE)
            stdout, _ = proc.communicate()
            self.assertEqual(str(stdout).strip('\n'), '[+] %s is not clean' % dirty)


class TestFileAttributes(unittest.TestCase):
    """
        test various stuffs about files (readable, writable, exist, ...)
    """

    def test_not_writtable(self):
        """ test MAT's behaviour on non-writable file"""
        proc = subprocess.Popen([MAT_PATH, 'not_writtable'],
                                stdout=subprocess.PIPE)
        stdout, _ = proc.communicate()
        self.assertEqual(str(stdout).strip('\n'), '[-] %s is not writable' % 'not_writtable')

    def test_not_exist(self):
        """ test MAT's behaviour on non-existent file"""
        proc = subprocess.Popen([MAT_PATH, 'ilikecookies'],
                                stdout=subprocess.PIPE)
        stdout, _ = proc.communicate()
        self.assertEqual(str(stdout).strip('\n'), 'Unable to process  %s' % 'ilikecookies')

    def test_empty(self):
        """ test MAT's behaviour on empty file"""
        proc = subprocess.Popen([MAT_PATH, 'empty_file'], stdout=subprocess.PIPE)
        stdout, _ = proc.communicate()
        self.assertEqual(str(stdout).strip('\n'), 'Unable to process  %s' % 'ilikecookies')


class TestUnsupported(test.MATTest):
    def test_abort_unsupported(self):
        """ test if the cli aborts on unsupported files
        """
        tarpath = os.path.join(self.tmpdir, "test.tar.bz2")
        tar = tarfile.open(tarpath, "w")
        for f in ('libtest.py', 'test.py', 'clitest.py'):
            tar.add(f, f)
        tar.close()
        proc = subprocess.Popen([MAT_PATH, tarpath], stdout=subprocess.PIPE)
        stdout, _ = proc.communicate()
        self.assertTrue('It contains unsupported filetypes:' \
                        '\n- libtest.py\n- test.py\n- clitest.py\n'
                        in str(stdout))


def get_tests():
    """ Return every clitests"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRemovecli))
    suite.addTest(unittest.makeSuite(TestListcli))
    suite.addTest(unittest.makeSuite(TestisCleancli))
    suite.addTest(unittest.makeSuite(TestUnsupported))
    return suite
