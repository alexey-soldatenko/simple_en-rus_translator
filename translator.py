import sqlite3

from custom_std import (
    clear_stdout_previous_characters,
    get_user_input,
)

ADD = "ADD"
TRANSLATE = "TRANSLATE"
PREVIOUS = "PREVIOUS"
NEXT = "NEXT"
HELP = "HELP"
QUIT = "QUIT"
UNKNOWN = "UNKNOWN"

SYSTEM_COMMAND = {
    "!add": ADD,
    "!quit": QUIT,
    "!help": HELP
}


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

    def get_system_command(self, phrase):
        cmd, *remainder = phrase.split()
        return SYSTEM_COMMAND[cmd], " ".join(remainder)

    def execute(self, command: str, **kwargs):
        method_name = "_run_{}_command".format(command)
        try:
            run_method = getattr(self, method_name)
        except AttributeError:
            raise NotImplementedError("Not implemented method for '{}' command".format(command))
        if callable(run_method):
            run_method(**kwargs)

    def _get_translation_from_db(self, word):
        with sqlite3.connect('en-rus.db') as conn:
            db_cursor = conn.cursor()
            db_cursor.execute("SELECT rus FROM dict where en='{}'".format(
                word))
            r = db_cursor.fetchone()
            return r[0] if r is not None else None

    def _run_add_command(self, user_input):
        eng, *translate = user_input.split()
        rus = " ".join(translate).strip()
        if self._get_translation_from_db(eng) is None and rus:
            with sqlite3.connect('en-rus.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO dict VALUES('{eng}', '{rus}')".format(
                    **vars()))
                print("\nWord added succefuly.")
        elif not rus:
            print("\nEnter translation please.")
        else:
            print("\nTranslation found for this word.")
        self.need_prompt = True

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


    def _run_translate_command(self, user_input):
        if user_input:
            with sqlite3.connect('en-rus.db') as conn:
                c = conn.cursor()

                translation = self._get_translation_from_db(user_input)
                if translation is not None:
                    colored_translation = "\x1b[96m{}\x1b[m".format(translation)
                    print("\n", colored_translation)
                else:
                    print("\nTranslation not found!")
                self._history.add(user_input)
        self.current_search_word = ""
        self.need_prompt = True


    def _run_next_command(self, user_input):
        if self._history.has_next():
            next_word = self._history.get_next(user_input)
            clear_stdout_previous_characters(len(user_input))
            self.current_search_word = next_word
            print(next_word, end="", flush=True)
        self.need_prompt = False


    def _run_previous_command(self, user_input):
        if self._history.has_previous():
            previous = self._history.get_previous(user_input)
            clear_stdout_previous_characters(len(user_input))
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

    def parse_and_execute(self, key_press: str, input_phrase: str):
        cmd = TRANSLATE
        if key_press == "ENTER" and input_phrase.startswith("!"):
            cmd, input_phrase = self._command.get_system_command(input_phrase)
        elif key_press == "UP":
            cmd = PREVIOUS
        elif key_press == "DOWN":
            cmd = NEXT
        self._command.execute(cmd.lower(), user_input=input_phrase)

    def execute_command(self, cmd, **kwargs):
        self._command.execute(cmd, **kwargs)

    def set_prompt_if_need(self):
        if self._command.need_prompt:
            print(">>>", end=" ", flush=True)

    def main_loop(self):
        self.execute_command("help")
        try:
            while True:
                self.set_prompt_if_need()
                input_phrase, key_press = get_user_input(self._command.current_search_word)
                self.parse_and_execute(key_press, input_phrase)
        except ExitCommand:
            print("\nBuy!")


    
def main():
    translator = Translator()
    translator.main_loop() 


if __name__ == '__main__':
    main()
