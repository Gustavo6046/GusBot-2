import plugincon
import re
import fnmatch
import json

def join_dicts(a, b):
    z = a.copy()
    z.update(b)
    return z
    

    
@plugincon.easy_bot_command("togglereplies")
def toggle_triggering(message, raw):
    if raw:
        return

    c = message["channel"]
    no_trigger_chans = json.load(open("aec.json"))
    
    if c in no_trigger_chans:
        no_trigger_chans.remove(c)
        
    else:
        no_trigger_chans.append(c)
        
    open("aec.json", "w").write(json.dumps(no_trigger_chans))
    return "Autoreply toggled succesfully on {}!".format(c)

@plugincon.easy_bot_command("autoreply", True)
def triggering(message, raw):
    if raw:
        return
        
    if len(message["arguments"]) < 5    :
        return "Syntax: autoreply <nickname mask> <message regex> | <reply>"

    n = message["arguments"].index("|")
    print n
    r = json.dumps(join_dicts(json.load(open("autoreplies.json")), {" ".join(message["arguments"][n + 1:]): (" ".join(message["arguments"][2:n]), message["arguments"][1])}))
    open("autoreplies.json", "w").write(r)

    return "Autoreply added succesfully!"

@plugincon.easy_bot_command("deautoreply", True)
def untriggering(message, raw):
    if raw:
        return

    r = json.load(open("autoreplies.json"))

    for k, (a, b) in r.items():
        if (a, b) == (" ".join(message["arguments"][2:]), message["arguments"][1]):
            del r[k]
            open("autoreplies.json", "w").write(json.dumps(r))

            return "Autoreply removed succesfully!"

    return "This autoreply is not there!"

@plugincon.easy_bot_command("lsautoreply")
def get_triggers(message, raw):
    if raw:
        return

    template = "Message matches regex '{body}' and nickname fnmatches '{nick}' then respond with '{answer}'."
    
    return ["Autoreplies: "] + [template.format(body=body, nick=nick, answer=answer) for answer, (body, nick) in json.load(open("autoreplies.json")).items()]

@plugincon.easy_bot_command("AUTOREPENGINE", all_messages=True)
def triggered(message, raw):
    if raw:
        return
        
    if message["channel"] in json.load(open("aec.json")):
        return

    results = []
        
    for k, v in json.load(open("autoreplies.json")).items():
        if not (re.match(v[0].lower(), message["message"].lower()) is None) and fnmatch.fnmatch(message["nickname"].lower(), v[1].lower()):
            print "Replying."
            results.append(k)

        else:
            print v[1].lower(), "!=", message["nickname"].lower(), "(match={})".format(message["nickname"].lower(), v[1].lower()), "||", v[0].lower(), "!=", message["message"].lower(), "match=({})".format(repr(re.match(v[0].lower(), message["message"].lower()))), ";;",

    print " "
    return results
