import requests
from typing import Optional


class APIError(Exception):
    pass


def get_translation(word: str) -> Optional[str]:
    origin_lang = "en"
    translated_lang = "ru"
    url = ("https://translate.googleapis.com/translate_a/single?client=gtx"
           "&sl={origin_lang}&tl={translated_lang}&dt=t&q={word}".format(**vars()))
    try:
        response = requests.get(url)
        response.raise_for_status()
        translated_word = response.json()[0][0][0]
        return translated_word.strip()
    except (requests.exceptions.HTTPError,
            requests.exceptions.Timeout,
            IndexError) as exc:
        raise APIError("Error occurs while request to online translator.")
    
