import sqlite3


class ExitCommand(Exception):
    pass


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


def is_command(word):
    return word.startswith('!')


def execute_command(command):
    if command == 'quit':
        raise ExitCommand()
    elif command == 'help':
        print_help()
    else:
        print("Unknown command!")


def main():
    with sqlite3.connect('en-rus.db') as conn:
        c = conn.cursor()
        print_help()
        while True:
            try:
                search = input(">>> ").strip()
                if not is_command(search):
                    translation = get_translation_from_db(search, c)
                    if translation is not None:
                        print("Translation:\n", translation)
                    else:
                        print("Translation not found!") 
                else:
                    execute_command(search[1:]) 
            except ExitCommand:
                print("Buy!")
                break


if __name__ == '__main__':
    main()
