import sqlite3

from custom_std import (
    clear_stdout_previous_characters,
    get_search_word_with_command,
    HELP,
    TRANSLATE,
    PREVIOUS,
    NEXT,
    QUIT,
    UNKNOWN)


def get_translation_from_db(word, db_cursor):
    db_cursor.execute("SELECT rus FROM dict where en='{}'".format(word))
    r = db_cursor.fetchone()
    return r[0] if r is not None else None


def print_help():
    s = """
---------------------------------------------
|    This is very simple en-rus translator. |
|                                           |
|    To execute command put '!' before.     |
|    For example: !quit, !help              |
---------------------------------------------
    """
    print(s)


def main():
    print_help()
    is_need_prompt = True
    word_on_screen = ""
    CACHE_PREVIOUS = []
    CACHE_NEXT = []
    while True:
        if is_need_prompt:
            print(">>>", end=" ", flush=True)
        search, cmd = get_search_word_with_command(word_on_screen)
        if cmd == QUIT:
            print("\nBuy!")
            break
        elif cmd == HELP:
            print_help()
            word_on_screen = ""
            is_need_prompt = True
        elif cmd == PREVIOUS:
            if CACHE_PREVIOUS:
                CACHE_NEXT.append(search)
                previous = CACHE_PREVIOUS.pop()
                clear_stdout_previous_characters(len(search))
                word_on_screen = previous
                print(previous, end="", flush=True)
            is_need_prompt = False
        elif cmd == NEXT:
            if CACHE_NEXT:
                CACHE_PREVIOUS.append(search)
                next_word = CACHE_NEXT.pop()
                clear_stdout_previous_characters(len(search))
                word_on_screen = next_word
                print(next_word, end="", flush=True)
            is_need_prompt = False
        elif cmd == TRANSLATE:
            with sqlite3.connect('en-rus.db') as conn:
                c = conn.cursor()

                translation = get_translation_from_db(search, c)
                if translation is not None:
                    print("\nTranslation:\n", translation)
                else:
                    print("\nTranslation not found!")
                word_on_screen = ""
                CACHE_PREVIOUS += CACHE_NEXT
                CACHE_PREVIOUS.append(search)
                CACHE_NEXT = []
                is_need_prompt = True
        elif cmd == UNKNOWN:
            print("\nNot valid command!\n")
            is_need_prompt = True

if __name__ == '__main__':
    main()
