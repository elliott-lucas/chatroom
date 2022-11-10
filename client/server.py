from threading import Thread
import socket
import time
from classes import *
from rsa import RSA
from aes import AES
import traceback

class Server():
	def __init__(self, app, ip, port, num, name="Server"):
		self.app             = app
		self.ip              = ip
		self.port            = port
		self.num             = num
		self.name            = name
		self.clients         = {}
		self.log             = []
		self.rsa             = RSA()
		self.aes             = AES()
		self.maxBytes        = 8192
		self.button          = None
		self.keyPublic       = None
		self.isOnline        = False
		self.isCurrentServer = False
		self.isClientTyping  = False
	def __eq__(self, other):
		return (self.ip == other.ip and self.port == other.port)
		
	def connect(self):
		h = "Connection"
		while self.isOnline == False:
			try:
				self.output(h, "Client Public Key  : %s" % self.app.keyPublicClient)
				self.output(h, "Client Private Key : %s" % self.app.keyPrivateClient)
				self.output(h, "Connecting to Server")
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.socket.connect((self.ip, self.port))
				self.isOnline = True
				self.button.serverStatus.configure(bg="green")
				self.output(h, "Connected to Server.")
				Thread(target=self.recieve, daemon=True).start()
				self.handshake()
				self.button.button.configure(state='normal')
				#Thread(target=self.ping, daemon=True).start()
			except Exception as E:
				self.socket.close()
				self.output(h, "Could Not connect. Retrying in 5 Seconds...")
				time.sleep(5)
	
	def disconnect(self):
		self.socket.close()
		self.isOnline = False
		self.button.serverStatus.configure(bg="red")
		self.keyPublic = None
		if self.isCurrentServer == True:
			for key, i in self.clients.items():
				self.app.ui.removeClientFrame(i.clientFrame, len(self.clients)-1)
		self.clients = {}
		self.app.handler.currentServer.button.configure(state='disabled')
		self.app.handler.changeServer(-1)
		
	def handshake(self):
		h = "Handshaker"
		self.output(h, "Waiting for Public Key from Server")
		while self.keyPublic == None:
			pass
		
		self.send("H", self.app.client.refID, "SERV", self.app.keyPublicClient, True)
		self.send("H", self.app.client.refID, "SERV", self.app.client.name, True)
		self.output(h, "handshake Complete.")
	
	def check(self, message):
		characters = list(message)
		messageOK = False
		for i in characters:
			if i not in [" ", "", "\n"]:
				messageOK = True
		return messageOK
	
	def ping(self):
		h = "Ping"
		while self.isOnline == True:
			self.startTime = time.time()
			self.output(h, "Pinging Server")
			self.send("P", self.app.client.refID, "SERV", "Ping", True)
			time.sleep(7)
	
	def send(self, mode, sender, recipient, data, encrypt):
		h = "Sender"
		messageObject = Message(mode, sender, recipient, data[:512], encrypt)
		if messageObject.mode == "M":
			self.app.ui.clear(["Input"])
		self.output(h, "Sending Message")
		serverMessageCache = messageObject
		if self.check(serverMessageCache.data) == True:
			messageEncrypted = self.encrypt(serverMessageCache, (serverMessageCache.encrypt, self.keyPublic))
			if serverMessageCache.recipient in ["SERV", "ALLC"]:
				self.socket.send(messageEncrypted)
			else:
				pass
			self.output(h, "Message Sent.")
			
	def recieve(self):
		h = "Reciever"
		handshakeRecieved = False
		while self.isOnline == True:
			try:
				fullMessageReceived = False
				messageEncrypted = b''
				while fullMessageReceived == False:
					messageEncrypted += self.socket.recv(1)
					if messageEncrypted.decode()[-1] == "|":
						fullMessageReceived = True
						print(messageEncrypted.decode())
						messageEncrypted = messageEncrypted[:-1]
				if handshakeRecieved == False:
					messageObject = self.decrypt(messageEncrypted, (False, None))
					handshakeRecieved = True
				else:
					messageObject = self.decrypt(messageEncrypted, (True, self.app.keyPrivateClient))
				if messageObject.mode == "H":
					self.keyPublic, self.name = messageObject.data.split("\n")
					self.output(h, "Server Public Key: %s" % self.keyPublic)
					self.output(h, "Server Name: %s" % self.name)
					self.button.button.configure(text=self.name)
				elif messageObject.mode == "M": #Message
					self.log.append(messageObject)
					if self.isCurrentServer == True:
						self.app.ui.displayMessage(messageObject, self.clients[messageObject.sender].name)
				elif messageObject.mode == "C": #Client Connect/Disconnect
					if messageObject.data[0] == "+":
						print(self.clients)
						print("Name: %s" % messageObject.data[5:])
						self.clients[messageObject.data[1:5]] = Client(messageObject.data[1:5], messageObject.data[5:])
						if self.isCurrentServer == True:
							self.clients[messageObject.data[1:5]].clientFrame = self.app.ui.createClientFrame(self.clients[messageObject.data[1:5]], len(self.clients))
							print("Made a client frame")
					elif messageObject.data[0] == "-":
						print(self.clients)
						if self.isCurrentServer == True:
							self.app.ui.removeClientFrame(self.clients[messageObject.data[1:5]].clientFrame, len(self.clients)-1)
						self.clients.pop(messageObject.data[1:5])
				elif messageObject.mode == "P":
					self.pingTime = int((time.time()-self.startTime)*100)
					if self.pingTime < 50:
						colour = "GREEN"
					elif self.pingTime < 100:
						colour = "ORANGE"
					else:
						colour = "RED"
					if self.isCurrentServer == True:
						self.app.ui.pingLabel.configure(text=("Ping: %s ms" % self.pingTime), fg=colour)
			except:
				self.output(h, "Server Offline, Attempting to Reconnect...")
				self.disconnect()
				self.connect()
				
	def encrypt(self, messageObject, RSA):
		if messageObject.mode in ["M","P"]:
			messageObject.data = self.aes.Encrypt(messageObject.data)
		messageText = messageObject.Construct()
		if RSA[0] == True:
			messageText = self.rsa.Encrypt(messageText, RSA[1])
		messageText = messageText.encode()
		return messageText
		
	def decrypt(self, messageText, RSA):
		messageText = messageText.decode()
		if RSA[0] == True:
			messageText = self.rsa.Decrypt(messageText, RSA[1])
		print("Raw String: %s" % messageText)
		messageObject = Message(messageText[0], messageText[1:5], messageText[5:9], messageText[9:], True)
		print(messageObject.data)
		if messageObject.mode in ["M","P"]:
			messageObject.data = self.aes.Decrypt(messageObject.data)
		return messageObject
		
	def output(self, handler, message):
		print("[%s]: %s" % (handler, message))
		pass

