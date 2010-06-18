#!/usr/bin/python
# -*- coding: utf-8 -*-
# Eli Criffield < pyeli AT zendo DOT net >
# Licensed under GPLv2 See: http://www.gnu.org/licenses/gpl.txt
#time.time()
# TODO: function for error message checking in __getURL
# TODO: real debug support, not just comments
# TODO: gui setup of config

import os
import sys
import ConfigParser
import getpass
import hashlib

class Config:

    """ SipieConf creates and reads the config file and can return 
      a dictionary for use with the Sipie Class
    """

    def __init__(self, confpath):
        """pass the location of the config directory
           like $HOME/.config/ 
           something like $HOME/.sipierc won't work (if thats a file)
           """

        self.execpted = ['username', 'password', 'login_type', 
                         'bitrate', 'canada', 'debug', 'cache', 'cache_min', 'mplayer']
        try:
            confdir = os.environ['XDG_CONFIG_HOME']
        except:
            confdir = '%s/.config' % os.environ['HOME']

        self.confpath = os.path.join(confdir, 'sipie')
        self.conffile = os.path.join(self.confpath, 'sipierc')
        self.config = ConfigParser.SafeConfigParser()

    def __makeMeSomeCookies(self):
        cookiepuss = """    # Netscape HTTP Cookie File
    # http://www.netscape.com/newsref/std/cookie_spec.html
    # This is a generated file!  Do not edit.

www.sirius.com	FALSE	/	FALSE		sirius_consumer_type	sirius_online_subscriber
www.sirius.com	FALSE	/	FALSE		sirius_login_type	subscriber
"""
        fd = open(os.path.join(self.confpath,'cookies.txt'), 'w')
        fd.write(cookiepuss)
        fd.close()
 
    def cryptPassword(self, password):
        """ used to convert the password to the type sirius wants
         and we don't have to store a plain password on disk """

        digest = hashlib.md5()
        digest.update(password)
        secret = digest.hexdigest()
        return secret

    def items(self):
        """ return a dictionary of items from the config
         use this to pass to the Sipie class
      """

        items = {}
        self.config.read(self.conffile)
        try:
            litems = self.config.items('sipie')
        except ConfigParser.NoSectionError:
            self.cliCreate() 
            litems = self.config.items('sipie')
        for (x, y) in litems:
            items[x] = y
        items['configpath'] = self.confpath
        return items

    def write(self):
        """ writes the config contents out  """

        fd = open(self.conffile, 'w')
        self.config.write(fd)
        fd.close()
        os.chmod(self.conffile, 448)

    def set(self, option, value):
        self.config.set('sipie', option, value)

    def cliCreate(self):
        """ if you don't have a config file this will ask the right questions 
      and create one, And it'll return a dictionary of the config like items() 
      would """

        print ''
        print 'username and an encrypted password will be stored in %s/config'%self.confpath
        print 'If you want to change your password remove %s/config'%self.confpath
        print "then run sipie and it'll ask you for username and password again"
        print ''
        if not os.path.isdir(self.confpath):
            os.mkdir(self.confpath)
        self.__makeMeSomeCookies()
        sys.stdout.write('Enter username: ')
        username = sys.stdin.readline().rstrip()
        password = self.cryptPassword(getpass.getpass('Enter password: '))
        print ''
        print 'Login Type, type guest or subscriber'
        sys.stdout.write('Enter login type: ')
        login_type = sys.stdin.readline().rstrip()
        while login_type not in ['subscriber', 'guest']:
            sys.stdout.write('Invalid: Enter login type: ')
            login_type = sys.stdin.readline().rstrip()
        sys.stdout.write('Are you using Sirius Cananda ')
        sys.stdout.write('(http://siriuscanada.ca)\n True or False: ')
        canada = sys.stdin.readline().rstrip().lower().capitalize()
        while canada not in ['True', 'False']:
            sys.stdout.write('Invalid: Enter True or False for canada: ')
            canada = sys.stdin.readline().rstrip().lower().capitalize()
        sys.stdout.write('Select bitrate')
        sys.stdout.write(' (High or Low): ')
        bitrate = sys.stdin.readline().rstrip().lower().capitalize()
        while bitrate not in ['High', 'Low']:
            sys.stdout.write('Invalid: Enter High or Low for bitrate: ')
            bitrate = sys.stdin.readline().rstrip().lower().capitalize()
        try:
            self.config.add_section('sipie')
        except ConfigParser.DuplicateSectionError:
            pass

        self.set('username', username)
        self.set('password', password)
        self.set('login_type', login_type)
        self.set('bitrate', bitrate)
        self.set('canada', canada)
        self.set('debug', 'False')
        self.set('cache', '32')
        self.set('cache_min', '4')
	self.set('mplayer', '/usr/bin/mplayer')
        self.write()
        return self.items()