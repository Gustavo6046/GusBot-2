import math
from core import bot_command

@bot_command("pi")
def get_pi(message, connector, index, plugin_list, raw):
    if not raw:
        connector.send_message(index, message["channel"], str(math.pi))

@bot_command("sine")
def sine_command(message, connector, index, plugin_list, raw):
    if not raw:
        try:
            connector.send_message(index, message["channel"], str(math.sin(message["arguments"][1])))

        except IndexError:
            connector.send_message(index, message["channel"], message["nick"] + ": No argument given!")

def register_plugin():
    return [get_pi]