from chatterbot.trainers import ListTrainer

import plugincon
import chatterbot
import re
import cson

chatters = {}
channel_messages = {}

chatters["John Default"] = chatterbot.chatterbot.ChatBot(
    "John Default",
    trainer='chatterbot.trainers.ListTrainer',
    logic_adapter='chatterbot.logic.BestMatch',
)

@plugincon.easy_bot_command("chb_init", True)
def start_chatterbot(message, raw):
    if raw:
        return

    if len(message["arguments"]) < 2:
        return "Syntax: chb_init <bot's name>"

    chatters[" ".join(message["arguments"][1:])] = chatterbot.chatterbot.ChatBot(
        " ".join(message["arguments"][1:]),
        trainer='chatterbot.trainers.ListTrainer',
        logic_adapter='chatterbot.logic.BestMatch',
    )

    return "ChatterBot made succesfully!"

@plugincon.easy_bot_command("chb_del", True)
def stop_chatterbot(message, raw):
    if raw:
        return

    if len(message["arguments"]) < 2:
        return "Syntax: chb_del <bot's name>"

    del chatters[" ".join(message["arguments"][1:])]

    return "ChatterBot deleted succesfully!"

@plugincon.easy_bot_command("chb")
def schatterbot(message, raw):
    if raw:
        return

    if len(message["arguments"]) < 4 or "|" not in message["arguments"]:
        return "Syntax: chb <bot's name> | <response string>"

    n = message["arguments"].index("|")

    if " ".join(message["arguments"][1:n]) not in chatters:
        return "No such chatter!"

    return "<{}> {}: {}".format(" ".join(message["arguments"][1:n]), message["nickname"], chatters[" ".join(message["arguments"][1:n])].get_response(" ".join(message["arguments"][n + 1:])))

@plugincon.easy_bot_command("CHB_LEARN", all_messages=True, dont_parse_if_prefix=True)
def chb_learner(message, raw):
    if raw:
        return

    if chatters == {}:
        return

    if len(message["arguments"]) < 1:
        return

    if type(message["message"]) is unicode:
        message["message"].encode("utf-8")

    if message["channel"] in channel_messages and len(channel_messages[message["channel"]]) > 1:
        try:
            n = channel_messages[message["channel"]].index([msg for msg in channel_messages[message["channel"]] if msg["nick"] != message["nickname"]][-1]) + 1
            alist = [x["msg"] for x in channel_messages[message["channel"]][n:]]
            answer = " | ".join(alist)

        except IndexError:
            if message["channel"] not in channel_messages:
                channel_messages[message["channel"]] = [{"msg": message["message"], "nick": message["nickname"]}]

            else:
                channel_messages[message["channel"]].append({"msg": message["message"], "nick": message["nickname"]})

            for c in chatters.values():
                c.train([channel_messages[message["channel"]][-1]["msg"], message["message"]])

            return

        try:
            if channel_messages[message["channel"]][-1]["nick"] == message["nickname"]:
                if message["channel"] not in channel_messages:
                    channel_messages[message["channel"]] = [{"msg": message["message"], "nick": message["nickname"]}]

                else:
                    channel_messages[message["channel"]].append({"msg": message["message"], "nick": message["nickname"]})

                for c in chatters.values():
                    c.train([channel_messages[message["channel"]][-1]["msg"], message["message"]])

                return

        except BaseException:
            print channel_messages[message["channel"]][-1]

            raise

        for c in chatters.values():
            c.train([channel_messages[message["channel"]][-1]["msg"], answer])

        for a in alist:
            tnick = re.match("^([a-zA-Z1-9-_|]): (.+)$", a)

            if tnick != None:
                nick = tnick.expand("\1")

                if nick not in [x["nick"] for x in channel_messages[message["channel"]]]:
                    for c in chatters.values():
                        c.train([channel_messages[message["channel"]][-1]["msg"], answer])

                else:
                    for c in chatters.values():
                        c.train([[x for x in channel_messages[message["channel"]] if x["nick"] == nick][-1]["msg"], tnick.expand("\2")])

    if message["channel"] not in channel_messages:
        channel_messages[message["channel"]] = [{"msg": message["message"], "nick": message["nickname"]}]

    else:
        channel_messages[message["channel"]].append({"msg": message["message"], "nick": message["nickname"]})
