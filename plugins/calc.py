import math
from plugincon import bot_command, easy_bot_command, get_message_target

@bot_command("pi")
def get_pi(message, connector, index, raw):
    if not raw:
        connector.send_message(index, get_message_target(connector, message, index), str(math.pi))

@easy_bot_command("sine")
def sine_command(message, raw):
    if not raw:
        try:
            try:
                return ["{}: {}".format(message["nickname"], str(math.sin(float(message["arguments"][1]))))]

            except ValueError:
                return [index,get_message_target(connector, message, index), message["nickname"] + ": Invalid literal!"]

        except IndexError:
            return [message["nickname"] + ": No argument given!"]

    else:
        return []


@easy_bot_command("cosine")
def cosine_command(message, raw):
    if not raw:
        try:
            print "Sending decimal cosine..."
            try:
                return [str(math.cos(float(message["arguments"][1])))]

            except ValueError:
                return [index, get_message_target(connector, message, index), message["nickname"] + ": Invalid literal!"]

        except IndexError:
            return [message["nickname"] + ": No argument given!"]

    else:
        return []
