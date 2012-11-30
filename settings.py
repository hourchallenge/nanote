import argparse
import ConfigParser
import os
import sys


def make_dir_if_not_exists(path):
    if not os.path.exists(path): os.makedirs(path)

home_dir = os.path.expanduser('~/.nanote/')
make_dir_if_not_exists(home_dir)
config_file_path = os.path.join(home_dir, 'settings')

defaults = {
            'path': os.path.join(home_dir, 'notes'),
            'default_note': '',
}

config = ConfigParser.SafeConfigParser(defaults)
config.read(config_file_path)

# get note search paths
# TODO: parse sys.argv arguments
args = {}
for arg in ('path', 'default_note'):
    if config.has_section('nanote'):
        args[arg] = config.get('nanote', arg)
    else:
        args[arg] = config.defaults()[arg]

NOTE_SEARCH_PATHS = '.:' + args['path']

NOTE_SEARCH_PATHS = [os.path.expanduser(p) for p in NOTE_SEARCH_PATHS.split(':')]


for path in NOTE_SEARCH_PATHS:
    make_dir_if_not_exists(path)

def find_note(note_name):
    # given a note name (i.e. school:homework), search {path}/school/homework for all 
    # paths on the note search path
    note_name = note_name.replace(':', '/')
    note_paths = [os.path.join(path, note_name) for path in NOTE_SEARCH_PATHS]
    for path in note_paths:
        if os.path.exists(path): return path
    return None