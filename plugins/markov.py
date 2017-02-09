import json
import BeautifulSoup
import requests
import re
import time
import threading
import networkx as nx
import multiprocessing
import matplotlib.pyplot as plt
import glob
import os
import difflib

from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname
from random import choice, sample

crawling = 0
crawled  = 0

markov_dict = {}
markov_filter = []

can_crawl = True

def hastebin(data):
    try:
        h = requests.post("http://hastebin.com/documents", data=data, timeout=10)

    except requests.exceptions.ConnectTimeout:
        return "\x01"

    if h.status_code != 200:
        return "\x02" + str(h.status_code)

    return "http://hastebin.com/" + h.json()['key']

def botbin(data, description="Result"):
    r = hastebin(data)

    if r == "\x01":
        return "Error: Connection to hastebin.com timed out!"

    elif r.startswith("\x02"):
        return "Error: Unsuccesful status code reached! ({})".format(r[1:])

    else:
        return "{} URL: {}".format(description, r)

@easy_bot_command("hastemarkovjson")
def hastemarkov(message, raw):
    if raw:
        return

    r = hastebin(json.dumps({x: list(y) for x, y in markov_dict.items()}, indent=4))

    if r == "\x01":
        return "Error: Connection to hastebin.com timed out!"

    elif r.startswith("\x02"):
        return "Error: Unsuccesful status code reached! ({})".format(r[1:])

    else:
        return "URL: {}".format(r)

@easy_bot_command("listmarkovfiles")
def list_markov_files(message, raw):
    if raw:
        return

    return botbin("\n".join([os.path.splitext(os.path.split(x)[-1])[0] for x in glob.glob("markov2/*.mkov2")]))

@easy_bot_command("qlistmarkovfiles")
def quick_list(message, raw):
    if raw:
        return

    return "Markov files that can be loaded using loadmarkov: {}".format(", ".join([os.path.splitext(os.path.split(x)[-1])[0] for x in glob.glob("markov2/*.mkov2")]))

@easy_bot_command("searchmarkovfiles")
def search_files(message, raw):
    if raw:
        return

    if len(message["arguments"]) < 2:
        return "Syntax: searchmarkofiles <keyword>"

    return "Similiar Markov files: {} | Markov files with {} in filename: {}".format(", ".join([x for x in [os.path.splitext(os.path.split(x)[-1])[0] for x in glob.glob("markov2/*.mkov2")] if difflib.SequenceMatcher(None, x, " ".join(message["arguments"][1:])).ratio() > 0.8]), message["arguments"][1], ", ".join(x for x in [os.path.splitext(os.path.split(x)[-1])[0] for x in glob.glob("markov2/*.mkov2")] if message["arguments"][1] in x))

@easy_bot_command("markovderivates")
def derivates(message, raw):
    if raw:
        return


    if len(message["arguments"]) < 2:
        return "Syntax: markovderivates <Markov keyword>"

    if message["arguments"][1] not in markov_dict:
        return "Error: No such word in Markov data!"

    return "Derivates for {}: {}".format(message["arguments"][1], ", ".join(markov_dict[message["arguments"][1]]))

def regex(value, reg):
    if reg == "":
        return True

    return bool(re.search(reg, value))


def ends_with_any(string, list_of_endings):
    for ending in list_of_endings:
        if string.endswith(ending):
            return True

    return False

def mkplot(markov_dict):
    G = nx.DiGraph()

    labels = {}

    for i, (k, v) in enumerate(markov_dict.iteritems()):
        G.add_node(k)

        for w in v:
            G.add_node(w)

    for i, (k, v) in enumerate(markov_dict.iteritems()):
        for w in v:
            G.add_edge(k, w)

    pos = nx.spring_layout(G)

    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_edges(G, pos, arrows=True)
    nx.draw_networkx_labels(G, pos, {w: w for k, v in markov_dict.items() for w in [x for x in [k] + list(v)]})

    plt.show()

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

def isalnumspace(string):
    for char in string:
        if not (char.isalnum() or " " == char):
            return False

    return True

def simple_string_filter(old_string, bad_chars=None, extra_filter=None):
    result = ""

    if bad_chars:
        for char in old_string:
            if not char in bad_chars:
                result += char

    if extra_filter and hasattr(extra_filter, "__call__"):
        old_result = result
        result = ""

        for char in old_result:
            if extra_filter(char):
                result += char

    return result

def parse_markov_string(string):
    global markov_dict

    words = simple_string_filter(string, "\'\"-/\\,.!?", isalnumspace).split(" ")

    for x in xrange(len(words)):
        try:
            if words[x - 1] == words[x] or words[x] == words[x + 1]:
                continue
        except IndexError:
            pass

        try:
            markov_dict[words[x - 1].lower()].add(words[x].lower())
        except KeyError:
            try:
                markov_dict[words[x - 1].lower()] = {words[x].lower()}
            except IndexError:
                pass
        except IndexError:
            pass

        try:
            markov_dict[words[x].lower()].add(words[x + 1].lower())
        except KeyError:
            try:
                markov_dict[words[x].lower()] = {words[x + 1].lower()}
            except IndexError:
                pass
        except IndexError:
            continue

def string_filter(old_string, filter_, separator=None):
    result_string = []

    if hasattr(filter_, "__call__"):
        for x in old_string:
            if filter_(x):
                result_string.append(x)

    else:
        if separator is None:
            for x in old_string:
                if x in str(filter_):
                    result_string.append(x)
        else:
            for x in old_string:
                if x in str(filter_).split(separator):
                    result_string.append(x)

    return "".join(result_string)

def crawl_markov(website, url_mask, max_level=3, level=0, crawled_urls=[]):
    global markov_dict
    global crawling, crawled

    crawling += 1

    if level > max_level:
        return

    if not can_crawl:
        return

    warnings = []
    time.sleep(0.4)

    try:
        request = requests.get(website.encode("utf-8"), timeout=10)

    except requests.ConnectionError:
        return

    except requests.exceptions.Timeout:
        return

    except (requests.exceptions.MissingSchema, requests.exceptions.InvalidURL):
        try:
            request = requests.get("http://" + website.encode("utf-8"), timeout=10)

        except requests.ConnectionError:
            return

        except requests.exceptions.Timeout:
            return

        except requests.exceptions.InvalidURL:
            return

    html = BeautifulSoup.BeautifulSoup(request.text.encode("utf-8"))

    for link in html.findAll("a", {"href": True}):
        url = link["href"].encode("utf-8'")

        if re.match("\.[a-zA-Z1-9]+$", url) and (not any(url.endswith(x) for x in [".html", ".php", ".htm"]) or "." in url.split("/")[-1]):
            continue

        if not url.startswith("http"):
            continue

        if url in crawled_urls:
            continue

        crawled_urls.append(url)

        if regex(url, url_mask):
            threading.Thread(target=crawl_markov, args=(url, url_mask, max_level, level+1, crawled_urls)).start()

    for visible_text in [text.encode("utf-8") for text in filter(visible, html.findAll(text=True))]:
        for line in visible_text.splitlines():
            parse_markov_string(line)

    time.sleep(0.5)
    crawled += 1

    print "Done crawling {}!".format(website)

@easy_bot_command("plotmarkov", True)
def plot_markov(message, raw):
    global markov_dict

    if raw:
        return

    p = multiprocessing.Process(target=mkplot, args=(markov_dict,))
    p.start()

    return "Plotting..."

@easy_bot_command("togglemarkovcrawling")
def toggle_crawling(message, raw):
    global can_crawl

    if raw:
        return

    can_crawl = not can_crawl

    return "Success: now crawling is{} stopped!".format(("n't" if can_crawl else ""))

@bot_command("parsemarkov", True)
def parse_markov_from_text(message, connector, index, raw):
    global markov_dict

    for key, item in markov_dict.items():
            markov_dict[key] = set(item)

    if not raw:
        if len(message["arguments"]) < 2:
            connector.send_message(index, get_message_target(connector, message, index), "{}: Error: No argument provided!".format(message["nickname"]))

        data = open(" ".join(message["arguments"][1:])).read()
        data = " ".join([n.strip() for n in data.split("\n")])

        words = [x for x in simple_string_filter(data, "\'\"-/\\,.!?", isalnumspace).split(" ") if x != " "]

        for x in xrange(len(words)):
            try:
                if words[x - 1] == words[x] or words[x] == words[x + 1]:
                    continue

            except IndexError:
                pass


            try:
                markov_dict[words[x - 1].lower()].add(words[x].lower())

            except KeyError:
                try:
                    markov_dict[words[x - 1].lower()] = {words[x].lower()}
                except IndexError:
                    pass

            except IndexError:
                pass


            try:
                markov_dict[words[x].lower()].add(words[x + 1].lower())

            except KeyError:
                try:
                    markov_dict[words[x].lower()] = {words[x + 1].lower()}
                except IndexError:
                    pass

            except IndexError:
                continue

        connector.send_message(index, get_message_target(connector, message, index), "{}: Text file succesfully parsed on Markov!".format(message["nickname"]))

@easy_bot_command("flushmarkov", True)
def flush_markov_data(message, raw):
    global markov_dict

    if raw:
        return

    markov_dict = {}

    return ["Markov flushed succesfully!"]

@easy_bot_command("mk_feeder", all_messages=True)
def feed_markov_data(message, raw):
    global markov_dict

    if raw:
        return

    for key, item in markov_dict.items():
            markov_dict[key] = set(item)

    words = simple_string_filter(" ".join(message["arguments"]), "\'\"-/\\,.!?", isalnumspace).split(" ")

    for x in xrange(len(words)):
        if x - 1 > -1:
            try:
                if words[x - 1] == words[x] or words[x] == words[x + 1]:
                    continue
            except IndexError:
                pass

            try:
                markov_dict[words[x - 1].lower()].add(words[x].lower())
            except KeyError:
                try:
                    markov_dict[words[x - 1].lower()] = {words[x].lower()}
                except IndexError:
                    pass
            except IndexError:
                pass

            try:
                markov_dict[words[x].lower()].add(words[x + 1].lower())
            except KeyError:
                try:
                    markov_dict[words[x].lower()] = {words[x + 1].lower()}
                except IndexError:
                    pass
            except IndexError:
                continue

        else:
            try:
                markov_dict[words[x].lower()].add(words[x + 1].lower())
            except KeyError:
                try:
                    markov_dict[words[x].lower()] = {words[x + 1].lower()}
                except IndexError:
                    pass
            except IndexError:
                continue

@easy_bot_command("markov")
def get_markov(message, raw):
    global markov_dict

    for key, item in markov_dict.items():
            markov_dict[key] = set(item)

    if raw:
        return

    # Checks.
    try:
        markov_dict.__delitem__("")
        markov_dict.__delitem__(" ")

    except KeyError:
        pass

    for i, mkv in markov_dict.items():
        try:
            markov_dict[i].remove(" ")
            markov_dict[i].remove("")

        except KeyError:
            continue

    if len(markov_dict) < 1:
        return "Error: no Markov data!"

    # Get the string!
    if len(message["arguments"]) < 2:
        x = choice(markov_dict.keys())
        words = [x]

    else:
        words = [x.lower() for x in message["arguments"][1:]]
        x = words[0]

    level = 0

    result = x

    print x

    while level < len(words) - 1:
        if not words[level + 1] in markov_dict[x]:
            return ["{}: {}".format(message["nickname"], result)]

        x = words[level + 1]
        level += 1
        result += " " + x

    while x in markov_dict.keys():
        try:
            x = sample(markov_dict[x], 1)[0]

        except ValueError:
            break

        print x.encode("utf-8")

        result += " " + x

        if len(result) > 750:
            break

    for cuss in markov_filter:
        result = result.replace(cuss, "*" * len(cuss))

    result = "{0}: {1}".format(message["nickname"], result)

    return [result]


@easy_bot_command("savemarkov", True)
def save_markov_json(message, raw):
    global markov_dict

    if not raw:
        if len(message["arguments"]) < 2:
            return ["Error: not enough arguments!", "(Insert Markov file name as an argument)"]

        save_dict = markov_dict

        for key, item in save_dict.items():
            save_dict[key] = tuple(item)

        open("markov2/{}.mkov2".format(message["arguments"][1]), "w").write(json.dumps(save_dict))

        for key, item in markov_dict.items():
            markov_dict[key] = set(item)

        return ["{}: Saved succesfully to {}.mkov2!".format(message["nickname"], message["arguments"][1])]

    else:
        return []

@easy_bot_command("loadmarkovfilter", True)
def load_markov_filter(message, raw):
    global markov_filter

    if raw:
        return

    if len(message["arguments"]) < 2:
        return ["Error: Not enough arguments!"]

    markov_filter += open("filters/{}.mkov2f".format(" ".join(message["arguments"][1:]))).readlines()

    return ["Blacklist updated succesfully!"]

@easy_bot_command("savemarkovfilter", True)
def save_markov_filter(message, raw):
    global markov_filter

    if raw:
        return

    if len(message["arguments"]) < 2:
        return ["Error: Not enough arguments!"]

    open("filters/{}.mkov2f".format(" ".join(message["arguments"][1:])), "w").write("\n".join(markov_filter))

    return ["Blacklist updated succesfully!"]

@easy_bot_command("loadmarkov", True)
def load_markov_json(message, raw):
    global markov_dict

    if not raw:
        if len(message["arguments"]) < 2:
            return ["Error: not enough arguments!", "(Insert Markov file name as an argument)"]

        new_dict = json.load(open("markov2/{}.mkov2".format(message["arguments"][1])))

        for key, item in new_dict.items():
            new_dict[key] = {word for word in item}

        markov_dict.update(new_dict)

        return ["Loaded succesfully from {}.mkov2!".format(message["arguments"][1])]

    else:
        return []

@easy_bot_command("listfiltermarkov")
def list_cusses(message, raw):
    if raw:
        return

    return "Cusses blacklisted: " + ", ".join(markov_filter)

@easy_bot_command("addfiltermarkov", True)
def filter_cusses(message, raw):
    if raw:
        return

    global markov_filter

    try:
        markov_filter += message["arguments"][1:]
        return ["Updated word blacklist succesfully!"]

    except IndexError:
        return ["Syntax: addfiltermarkov <list of cusses or blacklisted words>"]

@easy_bot_command("removefiltermarkov", True)
def unfilter_cusses(message, raw):
    if raw:
        return

    global markov_filter

    try:
        for cuss in message["arguments"][1:]:
            markov_filter.remove(cuss)

        return ["Updated word blacklist succesfully!"]

    except IndexError:
        return ["Syntax: removefiltermarkov <list of words to un-blacklist>"]

@easy_bot_command("parsewebmarkov")
def parse_web_markov(message, raw):
    global markov_dict

    for key, item in markov_dict.items():
            markov_dict[key] = set(item)

    if raw:
        return

    messages = []
    warnings = []

    debug = "--debug" in message["arguments"][1:]

    if len(message["arguments"]) < 2:
        return ["{}: Error: No argument provided! (Syntax: parsewebmarkov <list of URLs>)".format(message["nickname"])]

    for website in filter(lambda x: not x.startswith("--"), message["arguments"][1:]):
        print "Parsing Markov from {}!".format(website)
        messages.append("Parsing Markov from {}!".format(website))

        try:
            request = requests.get(website, timeout=10)

        except requests.ConnectionError:
            warnings.append("Error with connection!")

            if debug:
                    raise

        except requests.exceptions.Timeout:
            warnings.append("Connection timed out!")

            if debug:
                    raise

        except requests.exceptions.MissingSchema:
            try:
                request = requests.get("http://" + website, timeout=10)

            except requests.ConnectionError:
                warnings.append("Error with connection!")

                if debug:
                    raise

            except requests.exceptions.Timeout:
                warnings.append("Connection timed out!")

                if debug:
                    raise

        if not "request" in locals().keys():
            continue

        if request.status_code != 200:
            warnings.append("{}: Error: Status {} reached!".format(message["nickname"], request.status_code))
            continue

        visible_texts = [text.encode("utf-8") for text in filter(visible, BeautifulSoup.BeautifulSoup(request.text).findAll(text=True))]

        lines = []

        for text in visible_texts:
            lines += text.split("\n")

        for line in lines:
            words = simple_string_filter(line, "\'\"-/\\,.!?", isalnumspace).split(" ")

            for x in xrange(len(words)):
                try:
                    if words[x - 1] == words[x] or words[x] == words[x + 1]:
                        continue
                except IndexError:
                    pass

                try:
                    markov_dict[words[x - 1].lower()].add(words[x].lower())
                except KeyError:
                    try:
                        markov_dict[words[x - 1].lower()] = {words[x].lower()}
                    except IndexError:
                        pass
                except IndexError:
                    pass

                try:
                    markov_dict[words[x].lower()].add(words[x + 1].lower())
                except KeyError:
                    try:
                        markov_dict[words[x].lower()] = {words[x + 1].lower()}
                    except IndexError:
                        pass
                except IndexError:
                    continue

    if len(warnings) < len(message["arguments"][1:]):
        messages.append("{}: Success reading Markov from (some) website(s)!".format(message["nickname"]))

    return messages + warnings

@easy_bot_command("clearmarkovfilter", True)
def clear_filter(message, raw):
    global markov_filter

    if raw:
        return

    markov_filter = []
    return "Success clearing Markov filter!"

@easy_bot_command("purgemarkov", True)
def purge_word_from_markov(message, raw):
    global markov_dict

    if raw:
        return

    if len(message["arguments"]) < 2:
        return "Syntax: purgemarkov <list of words to purge from Markov>"

    for word in message["arguments"][1:]:
        for kw in markov_dict.keys():
            if kw == word:
                markov_dict.__delitem__(kw)

            try:
                if word in markov_dict[kw]:
                    markov_dict[kw] = [mk for mk in markov_dict[kw] if mk != word]

                    if markov_dict[kw] == []:
                        markov_dict.__delitem__(kw)

            except KeyError:
                pass

    return "Words purged from Markov succesfully!"

def check_crawled(connector, index, message):
    global crawling, crawled

    while crawling > crawled:
        time.sleep(0.2)

    connector.send_message(
        index,
        get_message_target(connector, message, index),
        "Finished crawling {all} websites!".format(all=crawled)
    )

@bot_command("parsewebmarkovcrawl", True)
def get_web_markov_crawling(message, connector, index, raw):
    global crawling, crawled

    def smsg(msg):
        if type(msg) is str:
            connector.send_message(
                index,
                get_message_target(connector, message, index),
                msg
            )

            return True

        elif hasattr(msg, "__iter__"):
            for m in msg:
                connector.send_message(
                    index,
                    get_message_target(connector, message, index),
                    m
                )

            return True

        else:
            return False

    crawling = 0
    crawled  = 0

    if raw:
        return

    time.sleep(0.3)

    if len(message["arguments"]) < 4:
        smsg("Syntax: <URL mask> <max level> <list of URLs to crawl for Markov>")
        return

    try:
        if int(message["arguments"][2]) > 4:
            smsg("Way too large value for max_level! Use only up to 4. Do you want to wait for an eternity?!?")
            return

        if int(message["arguments"][2]) < 0:
            smsg("Lol negative level XD")
            return

    except ValueError:
        smsg("Insert some int for max level (second argument)! Insert something between 0 and 4.")
        return

    for website in message["arguments"][3:]:
        crawl_markov(website, message["arguments"][1], int(message["arguments"][2]))

    smsg("Website crawling threads started! Check for new additions using ||markovsize .")

    threading.Thread(target=check_crawled, args=(connector, index, message)).start()

@easy_bot_command("markovsize")
def get_markov_size(message, raw):
    global markov_dict

    if not raw:
        return ["Size of Markov chain: {}".format(len(markov_dict))]
