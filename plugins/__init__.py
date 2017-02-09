import plugincon

pstate = {}

messages = [
    "Hey! This is not an easter egg! This is a dragon egg! Go away!",
    "*egg hatches* I warned!",
    "*stares as the hatchling feeds on {0}*",
    "*watches hidden as the hatchling burps*",
    "*stays hidden from the hatchling*",
    "*is found by the hatchling*",
    "*hatchling is full*",
    "*shivers and pets hatchling*",
    "*is licked by hatchling*",
    "*hugs hatchling*",
    "*stares as your corpse disappears and hears respawn sounds, and realizes; this is a multiplayer game!*",
    "*lets the hatchling go live it's adventures*",
    "*hears a random {0} stepping sounds and finds another egg*",
    "*finds you coming downstairs and staring the egg*"
]

@plugincon.easy_bot_command("__oops__")
def easter_egg(message, raw):
    if raw:
        return

    if message["nickname"] not in pstate:
        pstate[message["nickname"]] = 0

    else:
        pstate[message["nickname"]] += 1

    if pstate[message["nickname"]] >= len(messages):
        pstate[message["nickname"]] = 0

    return messages[pstate[message["nickname"]]].format(message["nickname"])
