from random import choice
from plugincon import bot_command, easy_bot_command, get_message_target

@easy_bot_command("hue")
def hue(message, raw):
    if not raw:
        return ["HUE!", "Go fuck yourself {}!".format(choice(["momma", "daddy"]))]
    else:
        return []