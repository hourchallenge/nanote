import settings

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
        
        if start_note:
            self.current_note = start_note
            self.load_note(start_note)
        else: 
            self.current_note = None
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
            if note_name is 'None':
                self.status = 'New note'
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
        self.status = '%s %s' % (self.history, self.history_position)
    
    def back(self):
        if self.history_position > 0:
            self.history_position -= 1
            self.load_note(self.history[self.history_position], going_back=True)
        self.status = '%s %s' % (self.history, self.history_position)
