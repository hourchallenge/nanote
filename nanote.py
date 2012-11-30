import curses
import re
import settings
from editor import Editor


shortcuts = [
             ('O', 'save'),
             ('X', 'quit'),
             ('N', 'new note'),
             ('G', 'goto note'),
             ('K', 'cut'),
             ('U', 'paste'),
             ('B', 'back'),
             ('F', 'forward'),
             ('T', 'settings'),
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

    

def main():
    screen = start_app()

    running = True

    default_note = settings.args['default_note']
    editor = Editor(default_note)

    end_state = None

    while running:
        try:
            screen_size = screen.getmaxyx()
            height, width = screen_size
            cy, cx = editor.cursor

            buffer_pad = curses.newpad(height, width)
            title_win = curses.newwin(1, width, 0, 0)
            shortcut_win = curses.newwin(3, width, height-3, 0)

            columns = int((len(shortcuts)+.5)/2)
            column_width = width / (columns + 1)
            for n, shortcut in enumerate(shortcuts):
                x = (n/2) * column_width
                y = 1 if not n%2 else 2
                shortcut_win.addstr(y, x, '^' + shortcut[0], curses.A_REVERSE)
                shortcut_win.addstr(' ' + shortcut[1])
            
            if editor.status:
                total_gap = width - len(editor.status) - 1
                left_gap = total_gap/2
                right_gap = total_gap-left_gap
                shortcut_win.addstr(0, 0, ' '*(left_gap) + editor.status + ' '*(right_gap), curses.A_REVERSE)
                editor.status = ''
                
            shortcut_win.refresh()

            note_name = editor.current_note if editor.current_note else 'untitled'
            title_text = 'nanote' + str(note_name)
            total_gap = width - len(title_text) - 1
            left_gap = total_gap/2
            right_gap = total_gap-left_gap
            title_win.addstr('nanote' + ' '*left_gap + str(note_name) + ' '*right_gap, curses.A_REVERSE)
            title_win.refresh()

            buffer_pad.addstr('\n'.join(editor.buffer))
            check_for_links_range = range(editor.pad_position[0], min(editor.pad_position[0] + height-3, editor.pad_position[0] + len(editor.buffer) - 1))
            links = []
            for n, i in enumerate(check_for_links_range):
                p = re.compile("\[[a-zA-Z\_\-\.\:]+\]")
                for m in p.finditer(editor.buffer[i]):
                    pos = m.start()
                    text = m.group()
                    buffer_pad.addstr(n, pos, text, curses.A_REVERSE)
                    if i == cy: links.append((pos, text))
            buffer_pad.refresh(editor.pad_position[0], editor.pad_position[1], 1, 0, height-4, width)

            screen.move(cy+1, cx)
            screen.refresh()

            c = screen.getch()
            handled_key = False
            for key, shortcut in shortcuts:
                if c == ord(key)-64:
                    if shortcut == 'quit':
                        running = False
                        
                    elif shortcut == 'save':
                        editor.save_note(editor.current_note)
                        
                    elif shortcut == 'goto note':
                        result = dialog('Enter the name of the note to load (^C to cancel):')
                        if result:
                            editor.load_note(result)
                            
                    elif shortcut == 'forward':
                        editor.forward()
                        
                    elif shortcut == 'back':
                        editor.back()
                        
                    elif shortcut == 'new note':
                        editor.load_note(None)
                        
                    elif shortcut == 'settings':
                        editor.load_note('**settings**')
                        
                    handled_key = True
            if not handled_key:
                if c == curses.KEY_UP:
                    editor.correct_cursor(cy-1, min(cx, len(editor.buffer[cy-1]) if 0 <= cy-1 < len(editor.buffer) else 0))
                elif c == curses.KEY_DOWN:
                    editor.correct_cursor(cy+1, cx)
                elif c == curses.KEY_LEFT:
                    editor.correct_cursor(cy, cx-1)
                elif c == curses.KEY_RIGHT:
                    editor.correct_cursor(cy, cx+1)
                elif c == ord('\n'):
                    follow_link = False
                    for pos, text in links:
                        if pos < cx < pos+len(text):
                            follow_link = text[1:-1]
                            current_note = follow_link
                            editor.load_note(current_note)
                    if not follow_link:
                        editor.altered = True
                        editor.buffer = editor.buffer[:cy] + [editor.buffer[cy][:cx]] + [editor.buffer[cy][cx:]] + editor.buffer[cy+1:]
                        editor.correct_cursor(cy+1, 0)
                elif c == curses.KEY_BACKSPACE:
                    editor.altered = True
                    if cy < len(editor.buffer[cy]):
                        if cx > 0:
                            editor.buffer[cy] = editor.buffer[cy][:cx-1] + editor.buffer[cy][cx:]
                        else:
                            editor.buffer = editor.buffer[:cy-1] + [editor.buffer[cy-1] + editor.buffer[cy]] + editor.buffer[cy+1:]
                    editor.correct_cursor(cy, cx-1)
                elif c == curses.KEY_DC:
                    editor.altered = True
                    if cy < len(editor.buffer[cy]):
                        if editor.buffer[cy]:
                            editor.buffer[cy] = editor.buffer[cy][:cx] + editor.buffer[cy][cx+1:]
                        else:
                            editor.buffer = editor.buffer[:cy] + editor.buffer[cy+1:]
                elif c == curses.KEY_HOME:
                    if cx == 0:
                        # TODO: smart home (go to first non-space character)
                        editor.correct_cursor(cy, cx)
                    else:
                        editor.correct_cursor(cy, 0)
                elif c == curses.KEY_END:
                    if cy < len(buffer):
                        editor.correct_cursor(cy, len(editor.buffer[cy]))
                # TODO: c<255? not all of those are good characters
                elif c < 255:
                    editor.altered = True
                    if cy > len(editor.buffer)-1: editor.buffer += ['']
                    editor.buffer[cy] = editor.buffer[cy][:cx] + chr(c) + editor.buffer[cy][cx:]
                    editor.correct_cursor(cy, cx+1)

        except KeyboardInterrupt:
            running = False
            
        except Exception as e:
            editor.status = 'exception: %s' % e
            end_state = editor.status
            running = False
        
    end_app(screen)
    if end_state: print end_state

if __name__ == '__main__':
    main()
