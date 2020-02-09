import requests
from typing import Optional


class APIError(Exception):
    pass


def get_translation(word: str) -> Optional[str]:
    url = ("https://translate.googleapis.com/translate_a/single?client=gtx"
           "&sl=en&tl=ru&dt=t&q={word}".format(word=word))
    try:
        response = requests.get(url)
        response.raise_for_status()
        translated_word = response.json()[0][0][0]
        translated_word = translated_word.lower().strip()
        result = translated_word if translated_word != word else None
        return result
    except (requests.exceptions.HTTPError,
            requests.exceptions.Timeout,
            IndexError) as exc:
        raise APIError("Online translate error: {}".format(exc))
    
