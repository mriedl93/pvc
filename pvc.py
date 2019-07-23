import argparse
import subprocess
import os
import json
import re


std_cfg = {
    'Audio-API': 'jack',
    'Playlists': [],
    'Deck Locking': True,
    '45': True,
    'Medium': 'serato_2a'
}


def argument_parser():
    parser = argparse.ArgumentParser(description='XWAX starter script v0.1')

    parser.add_argument('-a', '--playlist-append', dest='append', nargs=1, help='Add a playlist')
    parser.add_argument('-c', '--config', help='Spits out contents of config-file', action='store_true', default=False)
    parser.add_argument('-p', '--playlists', action='store_true', help='Prints out added playlists')
    parser.add_argument('-d', '--playlist-del', nargs=1, dest='delete', help='Deletes a playlist')
    parser.add_argument('-t', '--thru', nargs=1, help='Set THRU on Channel A or B')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Print out the start command without execution')

    args = parser.parse_args()
    main_prog(args)


def file_checker():
    file_check = os.path.isfile('./pvc.conf')
    if file_check:
        print("I found a config file... might as well use it then ;)")
    else:
        conf_writer(std_cfg)
        print("Created a new config file. Gonna exit now.")
        exit(0)


def conf_writer(conf):
    with open('pvc.conf', 'w') as cfg:
        json.dump(conf, cfg)


def conf_reader():
    with open('pvc.conf', 'r') as cfg:
        conf = json.load(cfg)
    return conf


def main_prog(args):

    file_checker()
    conf = conf_reader()

    # # # Print config
    if args.config:
        print(conf)

    # # # Append playlist
    elif args.append:
        if not os.path.isfile(args.append[0]):
            print('Error: Wrong input')
            exit(1)
        conf['Playlists'].append(args.append[0])
        conf_writer(conf)

    # # # Print Playlists
    elif args.playlists:
        for i, j in enumerate(conf['Playlists']):
            print(i, j)

    # # # Delete Playlist
    elif args.delete:
        if int(args.delete[0]) not in range(0, len(conf['Playlists'])):
            print('Error: Wrong input')
            exit(1)

    # # #  THRU
    elif args.thru:
        if args.thru[0] == 'a':
            chan_no = 'A'
        elif args.thru[0] == 'b':
            chan_no = 'B'
        else:
            print("Use either 'a' or 'b' as arguments")
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

    # # # Start xwax
    else:
        if conf['45']:
            revolutions = '-45'
        else:
            revolutions = '-33'
        if conf['Audio-API'] == 'jack':
            audio = '-j deckA -j deckB'
        else:
            audio = '-a ' + conf['Audio-API']
        if conf['Deck Locking']:
            lock = '-c'
        else:
            lock = '-u'

        plsts = []
        for i in conf['Playlists']:
            plsts.append('-l')
            plsts.append(i)
        
        starter = ['xwax', revolutions, lock, '-s', '/bin/cat', ' '.join(plsts), '-t', conf['Medium'], audio]

        if args.verbose:
            print(' '.join(starter))
        else:
            print(' '.join(starter))
            print("I would execute it now")
            # subprocess.call('xwax')


if __name__ == '__main__':
    argument_parser()
