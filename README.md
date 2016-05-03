# GusBot II
**The new top-hat bot for IRC, made entirely from scratch and GusPIRC**
----

# FAQ

## What is GusBot II?
It's an nice bot, powered by GusPIRC (and the new home of GusPIRC), ran over plugins and boasting a underlying .INI configuration system.

It does automatically connects to any number of servers specified in the INI file. It can easily be ran with the only command-line argument needed being the name of the .ini file without extension.

## How do I make the INI configuration file?

It usually looks somewhat like this:

    [General]
    NumServers=2
    Email=gugurehermann@gmail.com
    Master=Gustavo6046
    CommandPrefix=}:

    [Server0]
    URL=irc.freenode.net
    Port=6697
    Channels=#botters-test, #gusbot
    Nickname=GusBot2
    Password=<hidden>
    Account=GusBot
    AuthNumeric=376
    Authenticated=True

    [Server1]
    URL=irc.zandronum.com
    Port=6697
    Channels=#bottest
    Nickname=GusBot2
    Password=<hidden>
    Account=GusBot
    AuthNumeric=267
    Authenticated=True
    
## How do I make a plugin for it?

This is an simple example: (it'll probably suffice for now)

    @easy_bot_command()
    def my_commands_name(message, raw):
        if not raw:
            return ["Hello World!", "Second message.", "Third message! You said: " + " ".join(message["arguments"][1:])]
