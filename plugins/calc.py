from random import choice
import math
from main import bot_command, easy_bot_command


@bot_command("pi")
def get_pi(message, connector, index, raw):
    if not raw:
        connector.send_message(index, message["channel"], str(math.pi))


@bot_command("sine")
def sine_command(message, connector, index, raw):
    if not raw:
        try:
            connector.send_message(index, message["channel"], str(math.sin(message["arguments"][1])))

        except IndexError:
            connector.send_message(index, message["channel"], message["nick"] + ": No argument given!")


@bot_command("cosine")
def cosine_command(message, connector, index, raw):
    if not raw:
        try:
            connector.send_message(index, message["channel"], str(math.cos(message["arguments"][1])))

        except IndexError:
            connector.send_message(index, message["channel"], message["nick"] + ": No argument given!")

@easy_bot_command()
def hue(message, raw):
    if not raw:
        return ["HUE!", "Go fuck yourself {}!".format(choice(["momma", "daddy"]))]
    else:
        return []
