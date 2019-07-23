#!/usr/bin/env python3

"""
pvc - xwax starter script

A simple Python program to make xwax start-up a bit more dynamic and easy.
Simply run:

$ pvc

and on first startup it creates a default config, which you can edit easily.

Default config:
[xwax Options]
audio-api = jack                # Either jack or the name of the alsa device if you use alsa as API
deck locking = True             # Boolean: True or False
speed 45 rpm = True             # Boolean: True or False
medium = serato_2a              # Name of the medium you are using

[Playlists]
### Here will be a list of your playlists ###
### after you have added them ###


Important Info for Playlists:
It is assumed that you use 'xwax playlists', like those that can be exported from Amarok 2.
See http://wiki.xwax.org/ under External Tools the 'xwax playlist exporter' to see what I mean.
With this playlist exporter you get a playlist which can be scanned by cat and picked up by xwax.

Optional Arguments explained:

$ pvc -a [ID] [FILE/PATH]
Provide an ID as name of your playlist. Choose whatever you want here. You'll use this name for
the start-up with specific playlists with the -p option.

$ pvc -c
Prints out the contents of the config file.

$ pvc -p
$ pvc -p [ID] [ID] ...
If no Argument is provided, the program lists all added playlists in the format:
[ID] [FILE/PATH]
[ID] [FILE/PATH]
...
Use the names/IDs of playlists to start xwax with only those playlists. If this option is omitted
(basically just: $ pvc),
xwax will start with all added playlists.

$ pvc -d [ID]
Use this to delete a playlist from your config using the ID of the playlist.

$ pvc -t [a/b]
ONLY WORKS WITH TRAKTOR AUDIO 6!!!
Set Thru to Channel A or B respectively, ON or OFF.

$ pvc -v
Print out the start-command without execting it. Basically to see which
start-up command this script would produce.
"""


import argparse
import subprocess
import os
import json
import re
import configparser
import shlex


def argument_parser():
    parser = argparse.ArgumentParser(description='pvc - xwax starter script v0.2')

    parser.add_argument('-a', '--playlist-append', dest='append', nargs=2, help='Add a playlist; Format: -a [NAME] [FILE]')
    parser.add_argument('-c', '--config', help='Spits out contents of config-file', action='store_true', default=False)
    parser.add_argument('-p', '--playlists', nargs='*', default='all', help='Prints out all added playlists if no argument is provided.\nTakes the names of playlists as arguments to load only specific playlists into xwax.')
    parser.add_argument('-d', '--playlist-del', nargs=1, dest='delete', help='Deletes a playlist')
    parser.add_argument('-t', '--thru', nargs=1, help='Set THRU on Channel A or B; Requires a Traktor Audio 6')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Print out the start command without execution')

    args = parser.parse_args()
    main_prog(args)


def file_checker():
    file_check = os.path.isfile('./pvc-conf.ini')
    if file_check:
        print("I found a config file... might as well use it then ;)")
    else:
        conf_writer()
        print("Created a new config file. Gonna exit now.")
        exit(0)


def conf_writer():
    config = configparser.ConfigParser()
    config['xwax Options'] = {
        'audio-api': 'jack',
        'deck locking': True,
        'speed 45 rpm': True,
        'medium': 'serato_2a'
    }
    config['Playlists'] = {}
    with open('pvc-conf.ini', 'w') as cfg:
        config.write(cfg)


def main_prog(args):

    file_checker()
    config = configparser.ConfigParser()
    config.read('pvc-conf.ini')
    plsts = []

    # # # Print config
    if args.config:
        print(subprocess.call(['cat', 'pvc-conf.ini']))
        exit(0)

    # # # Append playlist
    elif args.append:
        if not os.path.isfile(args.append[1]):
            print('Error: Wrong input')
            exit(1)
        elif args.append[0] in config.options('Playlists'):
            print('Error: Name already in config')
            exit(1)

        config['Playlists'][args.append[0]] = args.append[1]
        with open('pvc-conf.ini', 'w') as cfg:
            config.write(cfg)
        exit(0)

    # # # Delete Playlist
    elif args.delete:
        if args.delete[0] not in config.options('Playlists'):
            print('Error: Wrong input')
            exit(1)

        config.remove_option('Playlists', args.delete[0])
        with open('pvc-conf.ini', 'w') as cfg:
            config.write(cfg)
        exit(0)

    # # #  THRU
    elif args.thru:
        if args.thru[0] == 'a':
            chan_no = 'A'
        elif args.thru[0] == 'b':
            chan_no = 'B'
        else:
            print("Use either 'a' or 'b' as arguments, for the respective channel")
            exit(1)

        # To get these lists parts of shell input: use module shlex' function split
        # e.g.: shlex.split('amixer -c T6 controls')
        amixer = subprocess.Popen(['amixer', '-c', 'T6', 'controls'], stdout=subprocess.PIPE)
        grep = subprocess.Popen(["grep", "'Direct Thru Channel {}'".format(chan_no)], stdin=amixer.stdout, stdout=subprocess.PIPE)
        cut = subprocess.Popen(["cut", "-d", ",", "-f", "1"], stdin=grep.stdout, stdout=subprocess.PIPE)
        output = subprocess.check_output(["cut", "-d", "=", "-f", "2"], stdin=cut.stdout)
        output = str(output)[2]

        am_status = subprocess.Popen(["amixer", "-c", "T6", "scontents"], stdout=subprocess.PIPE)
        grep2 = subprocess.check_output(["grep", "-A", "3", "'Direct Thru Channel {}".format(chan_no)], stdin=am_status.stdout)

        thru_active = re.search("\[on\]", str(grep2))  # returns boolean

        if thru_active:
            switch = 'off'
        else:
            switch = 'on'

        subprocess.call(["amixer", "-c", "T6", "cset", "numid={}".format(output), switch])
        print("Switching THRU on Channel {0} {1}".format(chan_no.upper(), switch))
        exit(0)

    # # # Print Playlists
    if config.options('Playlists') == []:
        print("Error: No Playlist in Config. Use 'pvc -a [ID] [FILE/PATH]' to add one.")
        exit(1)

    if args.playlists == []:
        for i in config['Playlists']:
            print(i, config['Playlists'][i])
        exit(0)
    elif args.playlists == 'all':
        for i in config['Playlists']:
            plsts.append('-l')
            plsts.append(config['Playlists'][i])
        start_xwax(config, plsts, args)
    else:
        for i in args.playlists:
            plsts.append('-l')
            plsts.append(config['Playlists'][i])
        start_xwax(config, plsts, args)


def start_xwax(config, plsts, args):

    if config['xwax Options'].getboolean('speed 45 rpm'):
        revolutions = '-45'
    else:
        revolutions = '-33'

    if config['xwax Options']['audio-api'] == 'jack':
        audio = '-j deckA -j deckB'
    else:
        audio = '-a ' + conf['Audio-API']
        
    if config['xwax Options'].getboolean('deck locking'):
        lock = '-c'
    else:
        lock = '-u'
    
    print(plsts)
    starter = shlex.split('xwax {} {} -s /bin/cat {} -t {} {}'.format(revolutions, lock, ' '.join(plsts), config['xwax Options']['medium'], audio))

    if args.verbose:
        print(' '.join(starter))
    else:
        subprocess.call(starter)


if __name__ == '__main__':
    argument_parser()
