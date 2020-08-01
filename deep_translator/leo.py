from deep_translator.constants import BASE_URLS, LINGUEE_LANGUAGES_TO_CODES, LINGUEE_CODE_TO_LANGUAGE
from deep_translator.exceptions import LanguageNotSupportedException, ElementNotFoundInGetRequest, NotValidPayload, NotValidLength
from deep_translator.parent import BaseTranslator
from bs4 import BeautifulSoup
import requests
from requests.utils import requote_uri


class LeoTranslator(BaseTranslator):
    supported_languages = list(LINGUEE_LANGUAGES_TO_CODES.keys())

    def __init__(self, source, target):
        """
        @param source: source language to translate from
        @param target: target language to translate to
        """
        self.__base_url = BASE_URLS.get("LEO")

        if self.is_language_supported(source, target):
            self._source, self._target = self._map_language_to_code(source.lower(), target.lower())

        super().__init__(base_url=self.__base_url,
                         source=self._source,
                         target=self._target,
                         element_tag='div',
                         element_query={'id': 'mainContent'},
                         payload_key=None,  # key of text in the url
                        )

    def _map_language_to_code(self, *languages, **kwargs):
        """
        @param language: type of language
        @return: mapped value of the language or raise an exception if the language is not supported
        """
        for language in languages:
            if language in LINGUEE_LANGUAGES_TO_CODES.values():
                yield LINGUEE_CODE_TO_LANGUAGE[language]
            elif language in LINGUEE_LANGUAGES_TO_CODES.keys():
                yield language
            else:
                raise LanguageNotSupportedException(language)

    def is_language_supported(self, *languages, **kwargs):
        for lang in languages:
            if lang not in LINGUEE_LANGUAGES_TO_CODES.keys():
                if lang not in LINGUEE_LANGUAGES_TO_CODES.values():
                    raise LanguageNotSupportedException(lang)
        return True

    def translate(self, word, **kwargs):

        if self._validate_payload(word):
            # %s-%s/translation/%s.html
            url = "{}{}-{}/translation/{}.html".format(self.__base_url, self._target, self._source, word)
            url = requote_uri(url)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            test = soup.select(selector='tbody tr td')
            print(test)
            for s in test:
                print(s)
            exit()
            elements = soup.find_all(self._element_tag, self._element_query)
            print(elements)
            res = []
            for el in elements:
                res.extend(el.find_all('a'))

            for r in res:
                print(r)
            exit()
            if not elements:
                raise ElementNotFoundInGetRequest(elements)

            if 'return_all' in kwargs and kwargs.get('return_all'):
                return [el.get_text(strip=True) for el in elements]
            else:
                return elements[0].get_text(strip=True)

    def translate_words(self, words, **kwargs):
        if not words:
            raise NotValidPayload(words)

        translated_words = []
        for word in words:
            translated_words.append(self.translate(payload=word))
        return translated_words


if __name__ == '__main__':
    res = LeoTranslator(source='english', target='german').translate('cute')