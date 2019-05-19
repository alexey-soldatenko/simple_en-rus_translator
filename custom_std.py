import termios
import sys
import tty


UP = b'\x1b[A'
DOWN = b'\x1b[B'
BACKSPACE = b'\x7f'
NEW_LINE = b'\n'


TRANSLATE = "TRANSLATE"
PREVIOUS = "PREVIOUS"
NEXT = "NEXT"
HELP = "HELP"
QUIT = "QUIT"
UNKNOWN = "UNKNOWN"

SYSTEM_COMMAND = {
    "!quit": QUIT,
    "!help": HELP
}


def get_bytes_from_stdin(number_bytes=1):
    return sys.stdin.buffer.read(number_bytes)


def write_byte_to_stdout(ch):
    sys.stdout.write(ch.decode())
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
        write_byte_to_stdout(b'\x1b[D\x1b[K')


@set_cbreak
def get_search_word_with_command(buf: str):
    command = TRANSLATE
    while True:
        ch = get_bytes_from_stdin()
        if buf and ch == NEW_LINE:
            break
        # printed characters
        if 31 < ord(ch) < 127:
            buf += ch.decode()
            write_byte_to_stdout(ch)
        if ch == BACKSPACE and buf:
            buf = buf[:-1]
            clear_stdout_previous_characters()
        # escape symbols
        if ord(ch) == 27:
            ch += get_bytes_from_stdin(number_bytes=2)
            if ch == UP:
                command = PREVIOUS
                break
            if ch == DOWN:
                command = NEXT
                break
    buf = buf.strip()
    if buf.startswith("!"):
        if buf in SYSTEM_COMMAND:
            command = SYSTEM_COMMAND[buf]
        else:
            command = UNKNOWN
    return buf, command

