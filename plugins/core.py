def bot_command(command_name):
    def real_decorator(func):
        def wrapper(message, connector, index, plugins, command_prefix):
            print message
            print command_prefix + command_name
            try:
                if message["body"].startswith(command_prefix + command_name):
                    func(message, connector, index, plugins, False)

            except KeyError:
                func(message, connector, index, plugins, True)

        return wrapper

    return real_decorator


@bot_command("addplugin")
def add_plugin(message, connector, index, plugins, raw):
    if not raw:
        return {"addplugins": [eval("plugins.{}".format(x)) for x in message["arguments"][1:]]}


@bot_command("pluginlist")
def list_plugins(message, connector, index, plugins, raw):
    if not raw:
        output = plugins[0].__name__

        for x in plugins[1:]:
            output += ", " + x.__name__

        connector.send_message(index, message["channel"], output)


def register_plugin():
    return [add_plugin, list_plugins]
