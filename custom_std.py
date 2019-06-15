import termios
import sys
import tty
import io


ESCAPE = '\x1b'
UP = '[A'
DOWN = '[B'
BACKSPACE = '\x7f'
NEW_LINE = '\n'


stdin_buffer = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8') 

def get_characters_from_stdin(char_count=1):
    return stdin_buffer.read(char_count)


def write_characters_to_stdout(ch):
    sys.stdout.write(ch)
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
        write_characters_to_stdout('\x1b[D\x1b[K')


@set_cbreak
def get_user_input(buf: str) -> tuple:
    """
    Return tuple with result user input and command.
    """
    command = "ENTER" 
    while True:
        ch = get_characters_from_stdin()
        if buf and ch == NEW_LINE:
            break
        elif ch == BACKSPACE:
            if buf:
                buf = buf[:-1]
                clear_stdout_previous_characters()
        elif ch == ESCAPE:
            esc_cmd = get_characters_from_stdin(char_count=2)
            if esc_cmd == UP:
                command = "UP"
                break
            if esc_cmd == DOWN:
                command = "DOWN"
                break
        else:
            buf += ch
            write_characters_to_stdout(ch)
    buf = buf.strip()
    return buf, command

