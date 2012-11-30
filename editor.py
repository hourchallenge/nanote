import settings

class Editor:
    def __init__(self, start_note):    
        self.cursor = (0,0)
        self.pad_position = (0,0)
        self.status = ''
        self.altered = False
        
        if start_note:
            self.current_note = start_note
            self.load_note(start_note)
        else: 
            self.current_note = None
            self.buffer = ['This is a test note.', '', 'You can link to other notes like this: [school:homework].', 'Put the cursor over a link and press ENTER to follow it.']

    
    
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
        
    def load_note(self, note_name):
        try:
            with open(settings.find_note(note_name)) as note_file:
                self.buffer = [r.rstrip('\n') for r in note_file.readlines()]
        except: self.buffer = []
        self.current_note = note_name
        self.cursor = (0,0)
        
    def save_note(self, note_name):
        note_path = settings.find_note(note_name)
        if not note_path: note_path = settings.default_note_path(note_name)
        directory = '/'.join(note_path.split('/')[:-1])
        settings.make_dir_if_not_exists(directory)
        with open(note_path, 'w') as note_file:
            note_file.write('\n'.join(self.buffer))
        self.status = 'Saved to %s' % note_path
        self.altered = False
