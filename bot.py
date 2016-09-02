from guspirc import IRCConnector
from ConfigParser import *
from threading import Thread

def connection(configuration_ini, connector=IRCConnector()):
	configuration = ConfigParser()
	threads = []

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
				
				try:
					use_ssl = configuration.getboolean("Server{}".format(i), "UseSSL")
					
				except NoOptionError:
					use_ssl = True
					
				master = configuration.get("General", "Master")
				has_account = configuration.getboolean("Server{}".format(i), "Authenticated")
				print "Got condition of authentication!"

			except (NoSectionError, NoOptionError):
				continue

			print "Connecting!"

			try:
				threads.append(Thread(name="Server {} Thread".format(server), target=connector.add_connection_socket, kwargs={
					"server": server,
					"port": port,
					"nickname": nick,
					"password": password,
					"use_ssl": use_ssl,
					"email": email,
					"account_name": account_name,
					"has_account": has_account,
					"channels": channels,
					"auth_numeric": authentication_number,
					"master": master
				}))
			except UnboundLocalError:
				print "Missing server section or option in the INI file!"
				continue

		for x in threads:
			x.daemon = True
			x.start()

		for x in threads:
			x.join()

		try:
			return [connector, configuration.get("General", "CommandPrefix")]

		except (NoSectionError, NoOptionError):
			return [connector, ""]

	except NoSectionError:
		return None