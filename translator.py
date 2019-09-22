import sqlite3

from command import Command, ExitCommand
from custom_io import get_user_input, Key


class Translator:
    def __init__(self):
        self._command = Command()

    def parse_and_execute(self, key_press: str, input_phrase: str):
        input_phrase = input_phrase.strip()
        cmd = self._command.TRANSLATE
        if key_press == Key.ENTER and input_phrase.startswith("!"):
            cmd, input_phrase = self._command.get_system_command(input_phrase)
        elif key_press == Key.UP:
            cmd = self._command.PREVIOUS
        elif key_press == Key.DOWN:
            cmd = self._command.NEXT
        self.execute_command(cmd, user_input=input_phrase)

    def execute_command(self, cmd, **kwargs):
        self._command.execute(cmd, **kwargs)

    def set_prompt_if_need(self):
        if self._command.need_prompt:
            print(">>>", end=" ", flush=True)

    def main_loop(self):
        self.execute_command("help")
        while True:
            try:
                self.set_prompt_if_need()
                input_phrase, key_press = get_user_input(self._command.current_search_word)
                self.parse_and_execute(key_press, input_phrase)
            except ExitCommand:
                print("\nBuy!")
                break
            except Exception as exc:
                print("\n", exc)


def main():
    translator = Translator()
    translator.main_loop() 


if __name__ == '__main__':
    main()
