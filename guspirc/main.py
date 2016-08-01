import time
import socket as skt

from Queue import Empty
from socket import SOCK_STREAM, socket, AF_INET, error
from threading import Thread
from time import sleep, strftime, time
from io import open
from iterqueue import IterableQueue
import ssl

docs = """
__________
|GusPIRC |
|\_\_\_\_|
|________|

The simple, event-driven (separate thread main loop), medium-level IRC lirary everyone wants.

To connect to IRC, all you have to do is to do a IRCConnector object and use the function
addSocketConnection() to add a connection to the server!

Then, parse all the messages received by receiveAllMessages() or just the latest one which
is returned by receiveLatestMessage()!
"""

disclaimer = """

Warning: Connecting to the same server and port multiple times may result in failure! This
module is no warranty that your bot will work. Much will depend in the modules that use
this interface!

Remember, this is a IRC INTERFACE, not a IRC BOT!

"""


# GusPIRC
#
# The simple, event-driven (main loop), low-level IRC library everyone wants


def log(logfile, msg):
	"""Logs msg to the log file.

	Reminder: msg must be a Unicode string!"""
	try:
		msg = msg.encode('utf-8')
		
	except (UnicodeDecodeError, UnicodeEncodeError):
		pass
		
	x = "[{0}]: {1}".format(strftime(u"%A %d - %X : GMT %Z"), msg)
	
	print x
	
	try:
		logfile.write(x.decode("utf-8") + "\n".decode("utf-8"))

	except (UnicodeDecodeError, UnicodeEncodeError):
		logfile.write(x)

class IRCConnector(object):
	"""The main connector with the IRC world!

	It must only be used once!

	And it's __init__ won't connect to a server by itself. Use
	add_connection_socket() function for this!"""

	def __init__(self):
		"""Are you really willing to call this?

		I though this was called automatically when you started the
		class variable!"""

		self.connections = []
		self.loopthreads = []

		self.logfile = open("log.txt", "a", encoding="utf-8")

		for n in xrange(len(self.connections)):
			self.loopthreads.append(Thread(target=self.main_loop, args=(n,)))

		for x in self.loopthreads:
			x.start()

	def add_connection_socket(self,
							  server,
							  port=6697,
							  ident="GusPIRC",
							  real_name="A GusPIRC Bot",
							  nickname="GusPIRC Bot",
							  password="",
							  email="email@address.com",
							  account_name="",
							  has_account=False,
							  channels=None,
							  auth_numeric=001,
							  master=""
							  ):
		"""Adds a IRC connection.

		Only call this ONCE PER SERVER! For multiple channels give a
		tuple with all the channel names as string for the argument channels!

		This function only works for NICKSERV-CONTAINING SERVERS!

		- server is the server address to connect to.
		Example: irc.freenode.com

		- port is the port of the server address.
		Example and default value: 6667

		- ident is the ident the bot's hostname will use! It's usually limited
		to 10 characters.

		Example: ident_here
		Result: connector.connections[index][4]!~ident_here@ip_here
		Default value: "GusPIRC"

		- real_name is the bot's real name d==played in most IRC clients.

		Example: GusBot(tm) the property of Gustavo6046

		- nickname is the nick of the bot (self-explanatory)

		Example: YourBotsName

		- password is the password of the bot.

		Example: password123bot

		USE WITH CAUTION! Don't share the password to anyone! Only to extremely
		trustable personnel! Only load it from a external file (like password.txt)
		and DON'T SHARE THE PASSWORD, IN SOURCE CODE, OR IN FILE!!!

		- email: the email the server should send the registration email to
		if has_account is set to False (see below!)

		Example and default value: email@address.com

		- account_name: is the name of the NickServ account the bot will
		use.

		Default value: ""

		Example: botaccount
		Default value: ""

		- has_account: is a bool that determines if the bot already has a reg==tered
		account.

		- channels: iterable object containing strings for the names of all the
		channels the bot should connect to upon joining the network.

		Example: (\"#botters-test\", \"#python\")
		Default value: None (== later defaulted to (\"#<insert bot's nickname here>help\"))

		- auth_numeric: the numeric after which the bot can auth.

		Defaults to 001, but it's a highly unrecommended numeric because it may result in
		the both authing as soon as it succesfully connects to the network.

		- master: the name of the admin of the bot. ToDo: add tuple instead of string
		for multiple admins"""

		if not hasattr(channels, "__iter__"):
			raise TypeError("channels == not iterable!")

		log(self.logfile, u"Iteration check done!")

		# | The following commented-out code is known to be faulty and thus
		# | was commented out.

		# if socket_index_by_address(server, port) != -1:
		#	  log(self.logfile, u"Warning: Trying to append socket of existing address!"
		#	  return False
		#
		# log(self.logfile, u"Check for duplicates done!"

		sock = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM))

		log(self.logfile, u"Socket making done!")

		try:
			sock.connect((server, int(port)))
			
		except skt.gaierror:
			return False

		log(self.logfile, u"Connected socket!")

		start_time = time()

		if not has_account:
			sock.sendall("NICK {0:s}\r\n".format(account_name))
			sock.sendall("USER {0:s} * * :{1:s}\r\n".format(ident, real_name))

		else:
			sock.sendall("PASS {0:s}:{1:s}\r\n".format(account_name.encode('utf-8'), password.encode('utf-8')))
			sock.sendall("USER {0:s} * * :{1:s}\r\n".format(ident, real_name))
			sock.sendall("NICK {0:s}\r\n".format(nickname))

		log(self.logfile, u"Sent first commands to socket!")

		# function used for breaking through all loops
		def waituntilnotice():
			"""This function is NOT to be called!
			It's a solution to the "break only inner loop" problem!"""
			buffering = u""
			while True:
				raw_received_message = sock.recv(1024).decode('utf-8')

				if raw_received_message == u"":
					time.sleep(0.2)
					continue

				if not raw_received_message.endswith(u"\r\n"):
					buffering += raw_received_message
					continue

				if buffering != u"":
					raw_received_message = u"%s%s" % (buffering, raw_received_message)
					buffering = ""

				y = raw_received_message.split(u"\r\n")
				y.pop(-1)

				for z in y:

					log(self.logfile, z.encode("utf-8"))

					try:
						compdata = z.split(" ")[1]
						
					except IndexError:
						time.sleep(0.2)
						continue
						
					if compdata == str(auth_numeric):
						return True

		if not waituntilnotice():
			return False

		log(self.logfile, u"NickServ Notice found!")

		if not has_account:
			sock.sendall(u"PRIVMSG NickServ :REGISTER {0:s} {1:s}\r\n".format(password, email))
			sock.sendall(u"PRIVMSG Q :HELLO {0:s} {1:s}\r\n".format(email, email))
			log(self.logfile, u"Made account!")

		try:
			sock.sendall("AUTH {0:s} {1:s}\r\n".format(account_name.encode('utf-8'), password[:10].encode('utf-8')))

		except IndexError:
			sock.sendall("AUTH {0:s} {1:s}\r\n".format(account_name.encode('utf-8'), password.encode('utf-8')))

		sock.sendall("NICK {0:s}\r\n".format(nickname.encode('utf-8')))

		if channels is None:
			channels = (u"#%shelp" % nickname,)
			log(self.logfile, u"Channel defaulting done!")
		else:
			log(self.logfile, u"Channel defaulting check done!")

		executed_time = time() - start_time

		sleep(10 - executed_time if executed_time < 10 else 2)

		for x in channels:
			sock.sendall("JOIN %s\r\n" % x.encode('utf-8'))

		if not has_account:
			sock.sendall("PASS {0:s}:{1:s}\r\n".format(account_name.encode('utf-8'), password.encode('utf-8')))
		sock.sendall(
			"PRIVMSG NickServ IDENTIFY {0:s} {1:s}\r\n".format(account_name.encode('utf-8'), password.encode('utf-8')))

		log(self.logfile, u"Joined channels!")

		sock.setblocking(0)

		self.connections.append([sock, IterableQueue(), IterableQueue(),
								 master, nickname, ident, server.split(u".")[1]])

		log(self.logfile, u"Added to connections!")

		return True

	def main_loop(self, index):
		"""It's the main loop mentioned in the docs.

		Call this in a while true loop, together with the rest!

		Parameters:
		- index: the index of the connector. Make sure you call th==
		therefore in a for loop for each IRC server connection!

		Like, for example:

		for x in xrange(len(connector.connectors)):
			connector.main_loop(x)"""

		if not self.connections:
			sleep(0.5)
			return

		else:
			x = self.connections[index]
			buffering = ""
			log(self.logfile, u"Set buffering to none")

			y = []

			while True:

				try:
					w = x[0].recv(4096).decode('utf-8')
				except error:
					if len(self.connections[index][2]) > 0:
						return
					else:
						sleep(0.1)
						continue

				if not (w.endswith(u"\n") or w.endswith(u"\r") or
							w.endswith(u"\r\n")):
					buffering = u"%s%s" % (buffering, w)
					continue

				if buffering != u"":
					w = u"%s%s" % (buffering, w)

				y = w.split(u"\n")
				y.pop(-1)

				break

			for z in y:
				log(self.logfile, z.encode("utf-8"))
				x[1].put(z.strip(u"\r"))
				if z.split(" ")[0] == u"PING":
					x[0].sendall("PONG :%s\r\n" % (z.split(":")[1].encode('utf-8')))
					log(self.logfile, u"Sent PONG")

				try:
					if z.split(" ")[0].strip(":") == u"QUIT":
						self.connections.pop(index)

				except IndexError:
					pass

			log(self.logfile, u"Ended loop!")

	def relay_out_queue(self, index=0):
		"""Call this after main_loop() and after parsing each of
		receiveAllMessages() messages.

		Parameters:
		- index: the index of the OutQueue (abbreviated OQ)"""

		log(self.logfile, u"Sending OQ messages!")

		worked = False

		try:
			v = self.connections[index][2].get(False).decode('utf-8')
			
			if v == u"":
				log(self.logfile, u"Error: Blank string in OQ!")
				return
				
			worked = True
			log(self.logfile, v)
			self.connections[index][0].sendall(v.encode('utf-8'))
			sleep(0.5)

		except Empty:
			if not worked:
				log(self.logfile, u"No OQ messages sent!")
				
			else:
				log(self.logfile, u"Sent all OQ messages!")
				sleep(0.5)
				
			pass

	def send_command(self, connection_index=0, command=""):
		"""Sends a command to the IRC server.

		- connection_index: the index of the connection. Usually in the order
		you called add_connection_socket().

		- command: the command string, including \":\" and \"PRIVMSG\" instead
		of \"MSG\" or \"SAY\". Don't include \"\\r\\n\", it's automatically added!"""
		self.connections[int(connection_index)][2].put("{0}\r\n".format(command.encode('utf-8')))

	def send_message(self,
					 connection_index=0,
					 target=u"ChanServ",
					 message=u"Error: No message argument provided to bot!"):
		"""Sends a message to the target in the IRC server.

		- connection_index: the index of the connection. Usually in the order
		you called add_connection_socket().

		- target: the target. Usually a channel name (like #python) (replaces SAY)
		or a nickname (replaces MSG).

		Defaults to sending ChanServ commands for a good reason!

		- message: the message sent to the target. Self-explanatory, I hope."""
		try:
			self.connections[connection_index][2].put_nowait(
				"PRIVMSG {0:s} :{1:s}\r\n".format(target.encode('utf-8'), message.encode('utf-8')))
		except UnicodeDecodeError:
			self.connections[connection_index][2].put_nowait("PRIVMSG {0:s} :{1:s}\r\n".format(target, message))

	def disconnect(
			self,
			connection_index=0,
			message="a GusPirc bot: The simplest Python low-level IRC interface"
	):
		"""D==connects from the server in the index specified.

		- connection_index: the index of the connection. Usually in the order
		you called add_connection_socket().

		- message: the quit message. Self-explanatory."""
		self.connections[connection_index][2].put_nowait("QUIT :%s\r\n" %
														 message.encode('utf-8'))

	def receive_latest_message(self, index=0):
		"""Returns the last message from the queue of received messages from
		the IRC socket.

		- index: the index of the connection. Ususally in the order you called
		add_connection_socket()."""
		try:
			return self.connections[index][1].get(False)
		except Empty:
			pass

	def send_notice(self, index=0, noticetarget="", msg=""):
		"""Sends a notice to noticetarget.

		Parameters:
		- index: the index of the connection. Usually in the order you called
		add_connection_socket().

		- noticetarget: which channel or whom to send the notice to.

		- msg: the notice's message to send."""

		self.send_command(index, "NOTICE %s :%s" % (noticetarget.encode('utf-8'), msg.encode('utf-8')))

	def socket_index_by_address(self, address, port=6667):
		"""Returns the index of the IRC connection that is connected to
		address:port or -1 if there aren't any."""
		if self.connections:
			for x in self.connections:
				if tuple(x[0].getsockname()[:2]) == [address, port]:
					return self.connections.index(x)
		return -1

	def receive_all_messages(self, index=0):
		"""Returns all the messages from the queue in the
		connection.

		- index: the index of the connection. Usually in the order you called
		add_connection_socket()."""

		messages = []

		while True:

			try:
				log(self.logfile, u"Receiving message!")
				messages.append(self.connections[index][1].get(False))
			except Empty:
				break

		return tuple(messages)
