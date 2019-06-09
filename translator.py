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


class ExitCommand(Exception):
    pass


class History:
    def __init__(self):
        self._previous = []
        self._next = []

    def add(self, word):
        self._previous += self._next
        self._previous.append(word)
        self._next = []

    def has_next(self):
        return bool(self._next)

    def has_previous(self):
        return bool(self._previous)

    def get_previous(self, current_word):
        self._next.append(current_word)
        return self._previous.pop()

    def get_next(self, current_word):
        self._previous.append(current_word)
        return self._next.pop()


class Command:
    def __init__(self):
        self._history = History()
        self.current_search_word = ""
        self.need_prompt = True

    def execute(self, command: str, **kwargs):
        method_name = "_run_{}_command".format(command)
        try:
            run_method = getattr(self, method_name)
        except AttributeError:
            raise NotImplementedError("Not implemented method for '{}' command".format(command))
        if callable(run_method):
            run_method(**kwargs)

    def _get_translation_from_db(self, word, db_cursor):
        db_cursor.execute("SELECT rus FROM dict where en='{}'".format(word))
        r = db_cursor.fetchone()
        return r[0] if r is not None else None


    def _run_help_command(self, **kwargs):
        s = ("\n---------------------------------------------\n"
             "|    This is very simple en-rus translator. |\n"
             "|                                           |\n"
             "|    To execute command put '!' before.     |\n"
             "|    For example: !quit, !help              |\n"
             "---------------------------------------------\n")
        print(s)
        self.current_search_word = ""
        self.need_prompt = True


    def _run_translate_command(self, search_word):
        with sqlite3.connect('en-rus.db') as conn:
            c = conn.cursor()

            translation = self._get_translation_from_db(search_word, c)
            if translation is not None:
                colored_translation = "\x1b[96m{}\x1b[m".format(translation)
                print("\n", colored_translation)
            else:
                print("\nTranslation not found!")
            self.current_search_word = ""
            self._history.add(search_word)
        self.need_prompt = True


    def _run_next_command(self, search_word):
        if self._history.has_next():
            next_word = self._history.get_next(search_word)
            clear_stdout_previous_characters(len(search_word))
            self.current_search_word = next_word
            print(next_word, end="", flush=True)
        self.need_prompt = False


    def _run_previous_command(self, search_word):
        if self._history.has_previous():
            previous = self._history.get_previous(search_word)
            clear_stdout_previous_characters(len(search_word))
            self.current_search_word = previous
            print(previous, end="", flush=True)
        self.need_prompt = False


    def _run_quit_command(self, **kwargs):
        raise ExitCommand()


    def _run_unknown_command(self, **kwargs):
        print("\nNot valid command!")
        self.need_prompt = True


class Translator:
    def __init__(self):
        self._command = Command()

    def execute_command(self, command: str, **kwargs):
        self._command.execute(command, **kwargs)

    def set_prompt_if_need(self):
        if self._command.need_prompt:
            print(">>>", end=" ", flush=True)

    def main_loop(self):
        self.execute_command("help")
        try:
            while True:
                self.set_prompt_if_need()
                search, cmd = get_search_word_with_command(self._command.current_search_word)
                self.execute_command(cmd.lower(), search_word=search)
        except ExitCommand:
            print("\nBuy!")


    
def main():
    translator = Translator()
    translator.main_loop() 


if __name__ == '__main__':
    main()
