from guspirc import IRCConnector
from ConfigParser import *

def connection(configuration_ini, connector=IRCConnector()):
    configuration = ConfigParser()

    for ini in configuration_ini:
        configuration.read(ini)

    try:
        for i in xrange(configuration.getint("General", "NumServers")):
            try:
                server = configuration.get("Server{}".format(i), "URL")
                print "Got server URL!"
                channels = configuration.get("Server{}".format(i), "Channels").split(", ")
                print "Got channel list!"
                port = configuration.getint("Server{}".format(i), "Port".format(i))
                print "Got port!"
                nick = configuration.get("Server{}".format(i), "Nickname".format(i))
                print "Got nick!"
                password = configuration.get("Server{}".format(i), "Password".format(i))
                print "Got password!"
                email = configuration.get("General", "Email")
                account_name = configuration.get("Server{}".format(i), "Account".format(i))
                print "Got account name!"
                authentication_number = configuration.getint("Server{}".format(i), "AuthNumeric".format(i))
                print "Got auth numeric!"
                master = configuration.get("General", "Master")
                has_account = configuration.getboolean("Server{}".format(i), "Authenticated")
                print "Got condition of authentication!"

            except (NoSectionError, NoOptionError):
                continue

            print "Connecting!"

            connector.add_connection_socket(
                server=server,
                port=port,
                nickname=nick,
                password=password,
                email=email,
                account_name=account_name,
                has_account=has_account,
                channels=channels,
                auth_numeric=authentication_number,
                master=master
            )

            return connector

    except NoSectionError:
        return None