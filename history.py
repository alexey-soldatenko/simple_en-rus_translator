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

