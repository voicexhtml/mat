#!/usr/bin/env python

import os

from distutils.core import setup, Command
from DistUtilsExtra.command import *

__version__ = '0.5.3'

# Remove MANIFEST file, since distutils
# doesn't properly update it when
# the contents of directories changes.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')


class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import sys
        os.chdir('test')
        errno = subprocess.call([sys.executable, 'test.py', '--local'])
        raise SystemExit(errno)

setup(
    name='MAT',
    version=__version__,
    description='Metadata Anonymisation Toolkit',
    long_description='A Metadata Anonymisation Toolkit in Python, using python-hachoir',
    author='jvoisin',
    author_email='julien.voisin@dustri.org',
    platforms='linux',
    license='GPLv2',
    url='https://mat.boum.org',
    packages=['libmat', 'libmat.hachoir_editor', 'libmat.bencode'],
    scripts=['mat', 'mat-gui'],
    data_files=[
        ('share/applications', ['mat.desktop']),
        ('share/mat', ['data/FORMATS', 'data/mat.glade']),
        ('share/pixmaps', ['data/mat.png']),
        ('share/doc/mat', ['README', 'README.security']),
        ('share/man/man1', ['mat.1', 'mat-gui.1']),
        ('share/nautilus-python/extensions', ['nautilus/nautilus-mat.py'])
    ],
    cmdclass={
        'test': PyTest,
        'build': build_extra.build_extra,
        'build_i18n': build_i18n.build_i18n,
        'build_help': build_help.build_help,
        'build_icons': build_icons.build_icons,
        'clean': clean_i18n.clean_i18n,
    },
    requires=['mutagen', 'gi', 'pdfrw', 'hachoir_core', 'hachoir_parser']
)
