import argparse
import ConfigParser
import os
import sys



shortcuts = [
             ('O', 'save'),
             ('X', 'quit'),
             ('N', 'new note'),
             ('G', 'goto note'),
             ('K', 'cut'),
             ('U', 'paste'),
             ('B', 'back'),
             ('F', 'forward'),
             ('W', 'find'),
             ('T', 'settings'),
             ]

def make_dir_if_not_exists(path):
    if not os.path.exists(path): os.makedirs(path)

home_dir = os.path.expanduser('~/.nanote/')
make_dir_if_not_exists(home_dir)
config_file_path = os.path.join(home_dir, 'settings')

defaults = [
            ('path', os.path.join(home_dir, 'notes')),
            ('default_note', ''),
            ('tab_width', '4'),
            ('link_re', '\[[a-zA-Z0-9\_\-\.\:\/]+\]'),
            ('bold_re', '\*[^ ^\[^\]^*^_][^\[^\]^*^_]*?\*'),
            ('underline_re', '\_[^ ^\[^\]^*^_][^\[^\]^*^_]*?\_'),
            ('bullet_re', '^ *\* .*'),
            ('bullet_symbols', '*o>-+'),
            ('comment_re', '\#.*'),
            ]

config = ConfigParser.SafeConfigParser()
if not config.has_section('nanote'): config.add_section('nanote')
for key, value in defaults:
    config.set('nanote', key, value)
config.read(config_file_path)
if not os.path.exists(config_file_path): 
    with open(config_file_path, 'w') as output_file:
        config.write(output_file)

# get note search paths
# TODO: parse sys.argv arguments
args = {}
for arg, _ in defaults:
    args[arg] = config.get('nanote', arg)
        
if len(sys.argv) > 1: args['default_note'] = sys.argv[1]
args['tab_width'] = int(args['tab_width'])

NOTE_SEARCH_PATHS = '.:' + args['path']

NOTE_SEARCH_PATHS = [os.path.expanduser(p) for p in NOTE_SEARCH_PATHS.split(':')]


for path in NOTE_SEARCH_PATHS:
    make_dir_if_not_exists(path)

def find_note(note_name):
    # given a note name (i.e. school:homework), search {path}/school/homework for all 
    # paths on the note search path
    if note_name == '**settings**': return config_file_path
    note_name = note_name.replace(':', '/')
    note_paths = [os.path.join(path, note_name) for path in NOTE_SEARCH_PATHS]
    for path in note_paths:
        if os.path.exists(path): return path
    return None
    
def default_note_path(note_name):
    note_name = note_name.replace(':', '/')
    return os.path.join(NOTE_SEARCH_PATHS[-1], note_name)
