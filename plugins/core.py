from importlib import import_module


def bot_command(command_name, admin_command=False):
    def real_decorator(func):
        def wrapper(message, connector, index, plugin_list, command_prefix, master):
            print message
            print command_prefix + command_name
            try:
                if message["arguments"][0] == command_prefix + command_name and (
                    not admin_command or message["nick"] == master
                ):
                    func(message, connector, index, plugin_list, False)

            except KeyError:
                func(message, connector, index, plugin_list, True)

        return wrapper

    return real_decorator


def message_parser():
    def real_decorator(func):
        def wrapper(message, connector, index, plugin_list):
            print message

            func()


@bot_command("eval", True)
def evaluate_expression(message, connector, index, plugin_list, raw):
    if not raw:
        connector.send_message(index, message["channel"], str(eval(" ".join(message["arguments"][1:]))))


@bot_command("addplugin")
def add_plugin(message, connector, index, plugin_list, raw):
    if not raw:
        result = {"addplugins": []}

        for x in message["arguments"][1:]:
            try:
                result["addplugins"].append(import_module("plugins." + x))

            except ImportError:
                connector.send_message(index, message["channel"], "Plugin {} not found!".format(x))

        connector.send_message(index, message["channel"], "Plugins loaded successfully!")
        return result


@bot_command("pluginlist")
def list_plugins(message, connector, index, plugin_list, raw):
    if not raw:
        output = plugin_list[0].__name__

        for x in plugin_list[1:]:
            output += ", " + x.__name__

        connector.send_message(index, message["channel"], output)


@bot_command("reload")
def reload_plugins(message, connector, index, plugin_list, raw):
    if not raw:
        return {"addplugins": plugin_list}


def register_plugin():
    return [add_plugin, list_plugins, reload_plugins, evaluate_expression]
