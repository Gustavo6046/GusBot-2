from random import choice
import math
from plugincon import bot_command, easy_bot_command

@bot_command("pi")
def get_pi(message, connector, index, raw):
    if not raw:
        connector.send_message(index, message["channel"], str(math.pi))
    else:
        return []


@easy_bot_command("sine")
def sine_command(message, raw):
    if not raw:
        try:
            print "Sending decimal sine..."
			
            try:
                return ["{}: {}".format(message["nick"], str(math.sin(Decimal(message["arguments"][1]))))]
				
            except InvalidOperation:
                return [index, message["channel"], message["nick"] + ": Invalid literal!"]

        except IndexError:
            return [message["nick"] + ": No argument given!"]

    else:
        return []


@easy_bot_command("cosine")
def cosine_command(message, raw):
    if not raw:
        try:
            print "Sending decimal cosine..."
            try:
                return [str(Decimal(math.cos(message["arguments"][1])))]
            except InvalidOperation:
                return [index, message["channel"], message["nick"] + ": Invalid literal!"]

        except IndexError:
            return [message["nick"] + ": No argument given!"]

    else:
        return []

@easy_bot_command("hue")
def hue(message, raw):
    if not raw:
        return ["HUE!", "Go fuck yourself {}!".format(choice(["momma", "daddy"]))]
    else:
        return []
