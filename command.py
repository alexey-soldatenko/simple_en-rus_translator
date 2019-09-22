import sqlite3

from custom_io import clear_stdout_previous_characters
from history import History
import online_translate


class CommandNotFoundError(Exception):
    pass

class ExitCommand(Exception):
    pass


class Command:
    TRANSLATE = "translate"
    PREVIOUS = "previous"
    NEXT = "next"

    SYSTEM_COMMAND = ["add", "cmdlist", "exit", "help"]

    def __init__(self):
        self._history = History()
        self.current_search_word = ""
        self.need_prompt = True

    def get_system_command(self, phrase):
        cmd, *remainder = phrase.split()
        cmd = cmd[1:]  # without '!'
        if cmd not in self.SYSTEM_COMMAND:
            raise CommandNotFoundError(
                "Command '{}' not found in {}".format(cmd, self.SYSTEM_COMMAND))
        return cmd, " ".join(remainder)

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

    def _get_translation_from_online(self, word):
        translated = online_translate.get_translation(word)
        if translated:
            self._save_to_db(word, translated)
        return translated

    def _save_to_db(self, origin, translated):
        if self._get_translation_from_db(origin) is None and translated:
            with sqlite3.connect('en-rus.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO dict VALUES('{origin}', '{translated}')".format(
                    **vars()))
                print("\nWord added succefuly.")
        elif not translated:
            print("\nEnter translation please.")
        else:
            print("\nTranslation found for this word.")

    def _run_cmdlist_command(self, **kwargs):
        print('\n', [k for k in sorted(self.SYSTEM_COMMAND)])
        self.current_search_word = ""
        self.need_prompt = True

    def _run_add_command(self, user_input):
        eng, *translate = user_input.split()
        rus = " ".join(translate).strip()
        self._save_to_db(eng, rus)
        self.need_prompt = True

    def _run_help_command(self, **kwargs):
        s = ("\n---------------------------------------------\n"
             "|    This is very simple en-rus translator. |\n"
             "|                                           |\n"
             "|    To execute command put '!' before.     |\n"
             "|    For example: !cmdlist                  |\n"
             "---------------------------------------------\n")
        print(s)
        self.current_search_word = ""
        self.need_prompt = True

    def _run_translate_command(self, user_input):
        if user_input:
            translation = self._get_translation_from_db(user_input)
            if not translation:
                translation = self._get_translation_from_online(user_input)

            if translation:
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

    def _run_exit_command(self, **kwargs):
        raise ExitCommand()

    def _run_unknown_command(self, **kwargs):
        print("\nNot valid command!")
        self.need_prompt = True

