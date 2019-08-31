import termios
import sys
import tty
import io


ESCAPE = '\x1b'
UP = '[A'
DOWN = '[B'
RIGHT = '[C'
LEFT = '[D'
BACKSPACE = '\x7f'
NEW_LINE = '\n'


stdin_buffer = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8') 


class Key:
    UP = "UP"
    DOWN = "DOWN"
    ENTER = "ENTER"


def get_characters_from_stdin(char_count=1):
    return stdin_buffer.read(char_count)


def write_characters_to_stdout(target_string):
    sys.stdout.write(target_string)
    sys.stdout.flush()


def set_cbreak(func):
    def wrapper(*args, **kwargs):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd, termios.TCSANOW)
            result = func(*args, **kwargs)
        finally:
            termios.tcsetattr(fd, termios.TCSANOW, old)
        return result
    return wrapper


def clear_stdout_previous_characters(num=1):
    for _ in range(num):
        move_cursor_to_left()
    # delete everything to the right of the cursor
    write_characters_to_stdout('\x1b[K')

def move_cursor_to_left(num=1):
    for _ in range(num):
        write_characters_to_stdout('\x1b[D')

def move_cursor_to_right(num=1):
    for _ in range(num):
        write_characters_to_stdout('\x1b[C')

@set_cbreak
def get_user_input(buf: str) -> tuple:
    """
    Return tuple with result user input and command.
    """
    command = Key.ENTER
    current_position = len(buf)
    while True:
        ch = get_characters_from_stdin()
        if ch == NEW_LINE:
            if buf.strip():
                break
        elif ch == BACKSPACE:
            if buf and current_position > 0:
                buf = buf[0:current_position - 1] + buf[current_position:]
                current_position -= 1
                clear_stdout_previous_characters()
                # add remaining part
                write_characters_to_stdout(buf[current_position:])
                # go to current position
                move_cursor_to_left(len(buf[current_position:]))
        elif ch == ESCAPE:
            esc_cmd = get_characters_from_stdin(char_count=2)
            if esc_cmd == UP:
                command = Key.UP
                break
            if esc_cmd == DOWN:
                command = Key.DOWN
                break
            if esc_cmd == LEFT:
                if current_position > 0:
                    current_position -= 1
                    move_cursor_to_left()
            if esc_cmd == RIGHT:
                if current_position < len(buf):
                    current_position += 1
                    move_cursor_to_right()
        else:
            new_str = ch + buf[current_position:]
            buf = buf[0:current_position] + new_str
            current_position += 1
            write_characters_to_stdout(new_str)
            move_cursor_to_left(len(new_str)-1)
    buf = buf.strip()
    return buf, command

