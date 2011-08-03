#!/usr/bin/python
'''
    Metadata anonymisation toolkit - CLI edition
'''

import sys
import xml.sax
import optparse

import hachoir_core

from lib import mat

__version__ = '0.1'


def parse():
    '''
        Get, and parse options passed to the program
    '''
    parser = optparse.OptionParser(usage='%prog [options] files')
    parser.add_option('--add2archive', '-a', action='store_true',
        default=False, help='Add to outputed archive non-supported filetypes')
    parser.add_option('--backup', '-b', action='store_true', default=False,
        help='Keep a backup copy')
    parser.add_option('--check', '-c',  action='store_true', default=False,
        help='Check if a file is free of harmfull metadatas')
    parser.add_option('--display', '-d', action='store_true', default=False,
        help='List all the meta of a file without removing them')
    parser.add_option('--list', '-l', action='store_true', default=False,
        help='List all supported fileformat')
    parser.add_option('--ugly', '-u', action='store_true', default=False,
        help='Remove harmful meta, but loss can occure')
    parser.add_option('--version', '-v', action='callback',
        callback=display_version, help='Display version and exit')

    values, arguments = parser.parse_args()
    if not arguments and values.list is False:
        parser.print_help()
        sys.exit(0)
    return values, arguments


def display_version(*_):
    '''
        Display the program's version, and exit
    '''
    print('Metadata Anonymisation Toolkit version %s') % mat.__version__
    print('CLI version %s') % __version__
    print('Hachoir version %s') % hachoir_core.__version__
    sys.exit(0)


def list_meta(class_file, filename):
    '''
        Print all the meta of 'filename' on stdout
    '''
    print('[+] File %s :' % filename)
    if class_file.is_clean():
        print('No harmful meta found')
    else:
        for key, value in class_file.get_meta().iteritems():
            print(key + ' : ' + str(value))


def is_clean(class_file, filename):
    '''
        Say if 'filename' is clean or not
    '''
    if class_file.is_clean():
        print('[+] %s is clean' % filename)
    else:
        print('[+] %s is not clean' % filename)


def clean_meta(class_file, filename):
    '''
        Clean the file 'filename'
    '''
    print('[+] Cleaning %s' % filename)
    if class_file.is_clean():
        print('%s is already clean' % filename)
    else:
        class_file.remove_all()
        print('%s cleaned !' % filename)


def clean_meta_ugly(class_file, filename):
    '''
        Clean the file 'filename', ugly way
    '''
    print('[+] Cleaning %s' % filename)
    if class_file.is_clean():
        print('%s is already clean' % filename)
    else:
        class_file.remove_all_ugly()
        print('%s cleaned' % filename)


def list_supported():
    '''
        Print all supported fileformat, and exit
    '''
    handler = mat.XMLParser()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    with open('FORMATS', 'r') as f:
        parser.parse(f)

    for item in handler.list:
        print('%s (%s)' % (item['name'], item['extension']))
        print('\tsupport : ' + item['support'])
        print('\tmetadata : ' + item['metadata'])
        print('\tmethod : ' + item['method'])
        if item['support'] == 'partial':
            print('\tremaining : ' + item['remaining'])
        print('\n')
    sys.exit(0)

def main():
    '''
        main function : get args, and launch the appropriate function
    '''
    args, filenames = parse()

    #func receive the function correponding to the options given as parameters
    if args.display is True:  # only print metadatas
        func = list_meta
    elif args.check is True:  # only check if the file is clean
        func = is_clean
    elif args.ugly is True:  # destructive anonymisation method
        func = clean_meta_ugly
    elif args.list is True:
        list_supported()
    else:  # clean the file
        func = clean_meta

    for filename in filenames:
        class_file = mat.create_class_file(filename, args.backup,
            args.add2archive)
        if class_file is not None:
            func(class_file, filename)

if __name__ == '__main__':
    main()
