import curses
import settings
import re


class Editor:
    def __init__(self, start_note):
        self.start_app()
        
        start_note = 'school:homework'
        self.cursor = (0,0)
        self.pad_position = (0,0)
        self.status = ''
        self.altered = False
        self.history = [None]
        self.history_position = 0
        self.links = []
        
        self.load_note(start_note)
        
        if start_note is None:
            self.buffer = ['This is a test note.', '', 'You can link to other notes like this: [school:homework].', 'Put the cursor over a link and press ENTER to follow it.']


    def start_app(self):
        # start the application
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)

    def end_app(self):
        # end the application
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()
        
    def draw_screen(self):
        screen_size = self.screen.getmaxyx()
        height, width = screen_size
        cy, cx = self.cursor

        buffer_pad = curses.newpad(height, width)
        title_win = curses.newwin(1, width, 0, 0)
        shortcut_win = curses.newwin(3, width, height-3, 0)

        columns = int((len(settings.shortcuts)+.5)/2)
        column_width = width / (columns + 1)
        for n, shortcut in enumerate(settings.shortcuts):
            x = (n/2) * column_width
            y = 1 if not n%2 else 2
            shortcut_win.addstr(y, x, '^' + shortcut[0], curses.A_REVERSE)
            shortcut_win.addstr(' ' + shortcut[1])
        
        if self.status:
            total_gap = width - len(self.status) - 1
            left_gap = total_gap/2
            right_gap = total_gap-left_gap
            shortcut_win.addstr(0, 0, ' '*(left_gap) + self.status + ' '*(right_gap), curses.A_REVERSE)
            self.status = ''
            
        shortcut_win.refresh()

        note_name = self.current_note if self.current_note else 'untitled'
        title_text = 'nanote' + str(note_name)
        total_gap = width - len(title_text) - 1
        left_gap = total_gap/2
        right_gap = total_gap-left_gap
        title_win.addstr('nanote' + ' '*left_gap + str(note_name) + ' '*right_gap, curses.A_REVERSE)
        title_win.refresh()

        buffer_pad.addstr('\n'.join(self.buffer))
        check_for_links_range = range(self.pad_position[0], min(self.pad_position[0] + height-3, self.pad_position[0] + len(self.buffer) - 1))
        self.links = []
        for n, i in enumerate(check_for_links_range):
            p = re.compile("\[[a-zA-Z\_\-\.\:]+\]")
            for m in p.finditer(self.buffer[i]):
                pos = m.start()
                text = m.group()
                buffer_pad.addstr(n, pos, text, curses.A_REVERSE)
                if i == cy: self.links.append((pos, text))
        buffer_pad.refresh(self.pad_position[0], self.pad_position[1], 1, 0, height-4, width)

        self.screen.move(cy+1, cx)
        self.screen.refresh()

        
    def dialog(self):
        pass

    
    def correct_cursor(self, cy, cx):
        buffer = self.buffer
        if cy < 0: 
            # up too far; move to top
            cy = 0; cx = 0
        if cy >= len(buffer): 
            # down too far; move to bottom
            cy = len(buffer)
        if cx < 0:
            # left too far; move up and to the end of the previous line
            return self.correct_cursor(cy-1, len(buffer[cy-1]))
        if (cy < len(buffer)) and (cx > len(buffer[cy])): 
            # right too far; move down and to the beginning of the next line
            return self.correct_cursor(cy+1, 0)
        if (cy >= len(buffer)) and cx > 0:
            cy = len(buffer); cx = 0
        self.cursor = (cy, cx)
        
    def load_note(self, note_name, going_back = False):
        try:
            if note_name is None:
                self.status = 'New note'
                self.buffer = []
            else:
                note_path = settings.find_note(note_name)
                with open(note_path) as note_file:
                    self.buffer = [r.rstrip('\n') for r in note_file.readlines()]    
                self.status = 'Loaded note %s from %s' % (note_name, note_path)
            if not going_back:
                self.history = self.history[:self.history_position+1] + [note_name]
                self.history_position = len(self.history) - 1
        except: 
            self.buffer = []
            self.status = "Couldn't find note %s" % note_name
        self.current_note = note_name
        self.cursor = (0,0)
        
    def save_note(self, note_name):
        note_path = settings.find_note(note_name)
        if not note_path: note_path = settings.default_note_path(note_name)
        directory = '/'.join(note_path.split('/')[:-1])
        settings.make_dir_if_not_exists(directory)
        with open(note_path, 'w') as note_file:
            note_file.write('\n'.join(self.buffer))
        self.status = 'Saved note %s to %s' % (note_name, note_path)
        self.altered = False
        self.current_note = note_name
        self.history[self.history_position] = note_name
        
    def forward(self):
        if self.history_position < len(self.history)-1:
            self.history_position += 1
            self.load_note(self.history[self.history_position], going_back=True)
    
    def back(self):
        if self.history_position > 0:
            self.history_position -= 1
            self.load_note(self.history[self.history_position], going_back=True)
