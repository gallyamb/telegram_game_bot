from bs4 import BeautifulSoup
from urllib import request, error
import re
import json
from time import sleep
import logging

logging.basicConfig(filename="bot.log", level=logging.INFO,
                    format="%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s")
logger = logging.getLogger(__name__)

base_url = r'http://www.zabytye-slova.ru/category/{0}/page/{1}'
letters = {'a': "а", 'b': "б", 'v': "в", 'g': "г", 'd': "д", 'e': "е", 'zh': "ж", 'z': "з",
           'i': "и", 'k': "к", 'l': "л", 'm': "м", 'n': "н", 'o': "о", 'p': "п", 'r': "р",
           's': "с", 't': "т", 'u': "у", 'f': "ф", 'x': "х", 'c': "ц", 'ch': "ч", 'sh': "ш",
           'shh': "щ", 'y': "ы", 'e-2': "э", 'yu': "ю", 'ya': "я"}
json_file_name = "definitions.json"


def is_adjective(word):
    return re.match(r"^.*(ой|ый|ий|ей|ая|ия|яя|ое|ие|ее)$", word) is not None


def get_definitions(letter):
    logger.info("Retrieving definitions for words that starts with '{0}'".format(letters[letter]))
    page_number = 1
    result = {}
    while True:
        try:
            page = request.urlopen(base_url.format(letter, str(page_number)))
            sleep(2)
        except error.HTTPError as e:
            if e.code == 404:
                break
            continue
        logger.info("Page {0} loaded".format(str(page_number)))
        page_number += 1
        for definition in BeautifulSoup(page, "html5lib").find_all("div", {"class": "post"}):
            definiendum = definition.find("div", {"class": "post-headline"}).find("a").text.strip()
            if is_adjective(definiendum):
                continue

            meaning = definition.find("div", {"class": "post-bodycopy"}).find("p").text.strip()
            match = re.match("^.*?это([^-.]*)[^-]*$", meaning)
            if not match:
                continue
            meaning = match.group(1).strip()
            result[definiendum] = meaning
    logger.info("{0} definitions found".format(len(result)))
    return result

definitions = {}

try:
    with open(json_file_name, 'r') as f:
        definitions.update(json.load(f))
    logger.info("Definitions loaded from disk")
except FileNotFoundError:
    logger.info("Definitions aren't found on a disk")
    for letter in letters.keys():
        definitions.update(get_definitions(letter))
    with open(json_file_name, 'w') as f:
        json.dump(definitions, f)

logger.info("{0} definitions at all".format(len(definitions)))
