from importlib import import_module
from main import bot_command, easy_bot_command


@bot_command("eval", True)
def evaluate_expression(message, connector, index, raw):
    if not raw:
        connector.send_message(index, message["channel"], str(eval(" ".join(message["arguments"][1:]))))