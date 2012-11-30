import curses
import time
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
    if cy < 0: cy = 0
    if cy >= len(buffer): 
        cy = len(buffer)
        cx = 0
    if cx < 0: 
        cy -= 1
        cx = len(buffer[cy])
        return correct_cursor(cy, cx, buffer)
    if (cy < len(buffer)) and (cx > len(buffer[cy])): 
        cy += 1
        cx = 0
        return correct_cursor(cy, cx, buffer)
    return (cy, cx)

def main():
    screen = start_app()

    running = True
    cursor = (0,0)
    pad_position = (0,0)

    default_note = settings.args['default_note']
    if default_note:
        current_note = default_note
        with open(settings.find_note(current_note)) as note_file:
            buffer = note_file.readlines()
    else: 
        current_note = None
        buffer = ['test', 'line 2', 'line 3', '', 'line 5']

    end_state = None

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

            screen.move(cursor[0]+1, cursor[1])
                
            shortcut_win.refresh()

            title_win.addstr('nanote', curses.A_REVERSE)
            title_win.refresh()

            buffer_pad.addstr('\n'.join(buffer))
            buffer_pad.refresh(pad_position[0], pad_position[1], 1, 0, height-4, width)

            screen.refresh()

            c = screen.getch()
            handled_key = False
            for key, shortcut in shortcuts:
                if c == ord(key)-64:
                    if shortcut == 'quit':
                        running = False
                    elif shortcut == 'save':
                        # TODO: write function to save notes
                        save_note(current_note, '\n'.join(buffer))
            if not handled_key:
                if c == curses.KEY_UP:
                    cursor = correct_cursor(cy-1, cx, buffer)
                elif c == curses.KEY_DOWN:
                    cursor = correct_cursor(cy+1, cx, buffer)
                elif c == curses.KEY_LEFT:
                    cursor = correct_cursor(cy, cx-1, buffer)
                elif c == curses.KEY_RIGHT:
                    cursor = correct_cursor(cy, cx+1, buffer)
                elif c == ord('\n'):
                    buffer = buffer[:cy] + [buffer[cy][:cx]] + [buffer[cy][cx:]] + buffer[cy+1:]
                    cursor = correct_cursor(cy+1, 0, buffer)

        except KeyboardInterrupt:
            running = False
            
        except Exception as e:
            end_state = e
            running = False
        
    end_app(screen)
    if end_state: print end_state

if __name__ == '__main__':
    main()