import curses
import re
import settings


shortcuts = [
             ('O', 'save'),
             ('X', 'quit'),
             ('N', 'new note'),
             ('G', 'goto note'),
             ('K', 'cut'),
             ('U', 'paste'),
             ('B', 'back'),
             ('F', 'forward'),
             ('S', 'settings'),
             ]

def start_app():
    # start the application; returns a curses screen
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(1)
    return screen

def end_app(screen):
    # end the application
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()

def correct_cursor(cy, cx, buffer):
    if cy < 0: 
        # up too far; move to top
        cy = 0; cx = 0
    if cy >= len(buffer): 
        # down too far; move to bottom
        cy = len(buffer)
    if cx < 0:
        # left too far; move up and to the end of the previous line
        return correct_cursor(cy-1, len(buffer[cy-1]), buffer)
    if (cy < len(buffer)) and (cx > len(buffer[cy])): 
        # right too far; move down and to the beginning of the next line
        return correct_cursor(cy+1, 0, buffer)
    if (cy >= len(buffer)) and cx > 0:
        cy = len(buffer); cx = 0
    return (cy, cx)
    
def load_note(note_name):
    try:
        with open(settings.find_note(note_name)) as note_file:
            return [r.rstrip('\n') for r in note_file.readlines()]
    except: return []
    
def save_note(note_name, buffer):
    note_path = settings.find_note(note_name)
    if not note_path: note_path = settings.default_note_path(note_name)
    directory = '/'.join(note_path.split('/')[:-1])
    settings.make_dir_if_not_exists(directory)
    with open(note_path, 'w') as note_file:
        note_file.write('\n'.join(buffer))
    return note_path

def main():
    screen = start_app()

    running = True
    cursor = (0,0)
    pad_position = (0,0)

    default_note = settings.args['default_note']
    if default_note:
        current_note = default_note
        buffer = load_note(current_note)
    else: 
        current_note = 'untitled'
        buffer = ['This is a test note.', '', 'You can link to other notes like this: [school:homework].', 'Put the cursor over a link and press ENTER to follow it.']

    end_state = None
    status = ''
    altered = False

    while running:
        try:
            screen_size = screen.getmaxyx()
            height, width = screen_size
            cy, cx = cursor

            buffer_pad = curses.newpad(height, width)
            title_win = curses.newwin(1, width, 0, 0)
            shortcut_win = curses.newwin(3, width, height-3, 0)

            columns = int((len(shortcuts)+.5)/2)
            column_width = width / (columns + 1)
            for n, shortcut in enumerate(shortcuts):
                x = (n/2) * column_width
                y = 1 if not n%2 else 2
                shortcut_win.addstr(y, x, ('^%s: %s' % shortcut))
            
            if status:
                total_gap = width - len(status) - 1
                left_gap = total_gap/2
                right_gap = total_gap-left_gap
                shortcut_win.addstr(0, 0, ' '*(left_gap) + status + ' '*(right_gap), curses.A_REVERSE)
                status = ''
                
            shortcut_win.refresh()

            title_text = 'nanote' + str(current_note)
            total_gap = width - len(title_text) - 1
            left_gap = total_gap/2
            right_gap = total_gap-left_gap
            title_win.addstr('nanote' + ' '*left_gap + str(current_note) + ' '*right_gap, curses.A_REVERSE)
            title_win.refresh()

            buffer_pad.addstr('\n'.join(buffer))
            check_for_links_range = range(pad_position[0], min(pad_position[0] + height-3, pad_position[0] + len(buffer) - 1))
            links = []
            for n, i in enumerate(check_for_links_range):
                p = re.compile("\[[a-zA-Z\_\-\.\:]+\]")
                for m in p.finditer(buffer[i]):
                    pos = m.start()
                    text = m.group()
                    buffer_pad.addstr(n, pos, text, curses.A_REVERSE)
                    if i == cy: links.append((pos, text))
            buffer_pad.refresh(pad_position[0], pad_position[1], 1, 0, height-4, width)

            screen.move(cursor[0]+1, cursor[1])
            screen.refresh()

            c = screen.getch()
            handled_key = False
            for key, shortcut in shortcuts:
                if c == ord(key)-64:
                    if shortcut == 'quit':
                        running = False
                        
                    elif shortcut == 'save':
                        # TODO: write function to save notes
                        save_result = save_note(current_note, buffer)
                        status = 'Saved to %s' % save_result
                        
                    handled_key = True
            if not handled_key:
                if c == curses.KEY_UP:
                    cursor = correct_cursor(cy-1, min(cx, len(buffer[cy-1]) if 0 <= cy-1 < len(buffer) else 0), buffer)
                elif c == curses.KEY_DOWN:
                    cursor = correct_cursor(cy+1, cx, buffer)
                elif c == curses.KEY_LEFT:
                    cursor = correct_cursor(cy, cx-1, buffer)
                elif c == curses.KEY_RIGHT:
                    cursor = correct_cursor(cy, cx+1, buffer)
                elif c == ord('\n'):
                    follow_link = False
                    for pos, text in links:
                        if pos < cx < pos+len(text):
                            follow_link = text[1:-1]
                            current_note = follow_link
                            buffer = load_note(current_note)
                            cursor = (0,0)
                    if not follow_link:
                        altered = True
                        buffer = buffer[:cy] + [buffer[cy][:cx]] + [buffer[cy][cx:]] + buffer[cy+1:]
                        cursor = correct_cursor(cy+1, 0, buffer)
                elif c == curses.KEY_BACKSPACE:
                    altered = True
                    if cy < len(buffer[cy]):
                        if cx > 0:
                            buffer[cy] = buffer[cy][:cx-1] + buffer[cy][cx:]
                        else:
                            buffer = buffer[:cy-1] + [buffer[cy-1] + buffer[cy]] + buffer[cy+1:]
                    cursor = correct_cursor(cy, cx-1, buffer)
                elif c == curses.KEY_DC:
                    altered = True
                    if cy < len(buffer[cy]):
                        if buffer[cy]:
                            buffer[cy] = buffer[cy][:cx] + buffer[cy][cx+1:]
                        else:
                            buffer = buffer[:cy] + buffer[cy+1:]
                elif c == curses.KEY_HOME:
                    if cx == 0:
                        # TODO: smart home (go to first non-space character)
                        cursor = correct_cursor(cy, cx, buffer)
                    else:
                        cursor = correct_cursor(cy, 0, buffer)
                elif c == curses.KEY_END:
                    if cy < len(buffer):
                        cursor = correct_cursor(cy, len(buffer[cy]), buffer)
                # TODO: c<255? not all of those are good characters
                elif c < 255:
                    altered = True
                    if cy > len(buffer)-1: buffer += ['']
                    buffer[cy] = buffer[cy][:cx] + chr(c) + buffer[cy][cx:]
                    cursor = correct_cursor(cy, cx+1, buffer)

        except KeyboardInterrupt:
            running = False
            
        except Exception as e:
            end_state = e
            running = False
        
    end_app(screen)
    if end_state: print end_state

if __name__ == '__main__':
    main()
