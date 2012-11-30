import curses
import time
import settings

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
    cursor = (0,0)
    while running:
        try:
            screen_size = screen.getmaxyx()
        except KeyboardInterrupt:
            running = False
        
    end_app(screen)

if __name__ == '__main__':
    main()