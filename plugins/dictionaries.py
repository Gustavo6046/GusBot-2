import json
import plugincon
import os
import difflib
import glob
import urbandictionary as ud
import pastebin as pb
import requests

aliases = {}
dictionary_cache = {os.path.split(os.path.splitext(n)[0])[-1]: {x.lower(): y for x, y in json.load(open(n)).iteritems()} for n in glob.glob("dictionaries/*.json")}

def enumerated_join(iterable, start=0, step=1, sep=" | ", skip_if_one=True, enumeration_sep=".", default=None):
    if len(iterable) == 1 and skip_if_one:
        return iterable[0]

    elif len(iterable) <= 0:
        return default

    result = []

    for i, x in enumerate(iterable):
        result.append("{}{} {}".format(i * step + start, enumeration_sep, x))

    return sep.join(result)

@plugincon.easy_bot_command("udict_get")
def urban_dict(message, raw):
    if raw:
        return

    if len(message["arguments"]) < 2:
        return "Syntax: udict_get <term>"

    word = " ".join(message["arguments"][1:]).lower()

    if word == " ":
        return "Syntax: udict_get <term>"

    try:
        results = enumerated_join([u"{definition} (u{upvotes}d{downvotes}) -- Example: {example}".format(**d.__dict__) for d in ud.define(word)], start=1, sep="\n\n", default="Error: No definition!")
        result = []
        sr = ""

    except IndexError:
        return "Error: No definition!"

    for r in results.split(" "):
        sr += r + " "

        if len(sr) > 100:
            result.append(sr)
            sr = ""

    if result[-1] != sr:
        result.append(sr)

    try:
        req = requests.post("http://hastebin.com/documents", data="\n".join(result), timeout=10)

    except requests.exceptions.ConnectTimeout:
        return "Connection to hastebin timed out!"

    if req.status_code == 200:
        return "Definition URL from Hastebin: http://hastebin.com/{}".format(req.json()['key'])

    else:
        return "Error status code! ({})".format(hastebin.status_code)

@plugincon.easy_bot_command("dict_alias")
def alias_dictionary(message, raw):
    if raw:
        return

    try:
        for alias in message["arguments"][2:]:
            aliases[alias] = message["arguments"][1]

    except IndexError:
        return "Syntax: dict_alias <target> <alias> [<alias> [...]]"

@plugincon.easy_bot_command("dict_get")
def get_from_dictionary(message, raw):
    if raw:
        return

    if len(message["arguments"]) < 3:
        return "Syntax: dict_get <dictionary name> <word to scan in dictionary>"

    dictionary = message["arguments"][1].lower()
    word = " ".join(message["arguments"][2:]).lower()

    if word in ("", " "):
        return "Syntax: dict_get <dictionary name> <word to scan in dictionary>"

    alias_path = [dictionary]

    while dictionary not in dictionary_cache:
        if dictionary not in aliases:
            return "No such dictionary or dictionary alias! (Path: {})".format(" -> ".join(alias_path))

        dictionary = aliases[dictionary]

        if len(alias_path) > 30:
            return "Max alias depth reached! Did you make an alias loop? (Path: {})".format(" -> ".join(alias_path))

        alias_path.append(dictionary)

    try:
        if type(dictionary_cache[dictionary][word]) in (str, unicode):
            try:
                return "Definitions: {}".format(dictionary_cache[dictionary][word].encode("utf-8"))

            except UnicodeDecodeError:
                return "Definitions: {}".format(dictionary_cache[dictionary][word])

        elif hasattr(dictionary_cache[dictionary][word], "__iter__"):
            try:
                return "Definitions: {}".format(enumerated_join([x.encode("utf-8") for x in dictionary_cache[dictionary][word]], start=1, default="Error: No definition in list!"))

            except UnicodeDecodeError:
                return "Definitions: {}".format(enumerated_join(dictionary_cache[dictionary][word], start=1, default="Error: No definition in list!"))

        else:
            return "Error: Definitions in a non-interable and non-stringable format ({})!".format(type(dictionary_cache[dictionary][word]))

    except KeyError:
        return "Error: No such word in dictionary specified! Similar words: {}".format(", ".join(x for x in dictionary_cache[dictionary].keys() if difflib.SequenceMatcher(None, x, word).ratio() > 0.7))

@plugincon.easy_bot_command("dict_add")
def add_to_dict(message, raw):
    global dictionary_cache

    if raw:
        return

    try:
        dictionary = message["arguments"][1]
        word = " ".join(message["arguments"][2:]).split("|")[0].strip()
        definition = "|".join(" ".join(message["arguments"][2:]).split("|")[1:]).strip()

    except IndexError:
        return [
            "Syntax: dict_add <dictionary name> <word>|<definition>",
            "The '|' is REQUIRED between the word and definition to prevent confusion!"
        ]

    if dictionary not in dictionary_cache:
        return "Error: No such dictionary!"

    try:
        dictionary_cache[dictionary][word].append(definition)

    except KeyError:
        dictionary_cache[dictionary][word] = [definition]

@plugincon.easy_bot_command("dict_remove")
def add_to_dict(message, raw):
    if raw:
        return

    try:
        dictionary = message["arguments"][1]
        word = " ".join(message["arguments"][2:]).split("|")[0].strip()
        definition = "|".join(" ".join(message["arguments"][2:]).split("|")[1:]).strip()

    except IndexError:
        return "Syntax: dict_remove <dictionary name> <word>"

    if dictionary not in dictionary_cache:
        return "Error: No such dictionary!"

    try:
        del dictionary_cache[dictionary][word]

    except KeyError:
        return "No such word already!"

@plugincon.easy_bot_command("dict_list")
def list_dictionaries(message, raw):
    if raw:
        return

    return "Dictionaries cached: " + ", ".join(dictionary_cache.keys()) + "; Aliases: " + ", ".join(["{} -> {}".format(x, y) for x, y in aliases.items()])
