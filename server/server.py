import socket
import datetime
import time
from classes import *
from threading import Thread
from rsa import RSA

class Server():
	def __init__(self, ip, port, name="Server"):
		self.ip         = ip
		self.port       = port
		self.name       = name
		self.clients    = {}
		self.queue      = []
		self.rsa		= RSA()
		self.maxBytes	= 8192
		self.keyPublic	= None
		self.keyPrivate	= None
		self.isOnline	= False

	def start(self):
		h = "Startup"
		self.output(h, "Generating Public/Private Key")
		self.keyPublic, self.keyPrivate = self.rsa.keyGen()
		
		self.output(h, "Server Public Key  : %s" % self.keyPublic)
		self.output(h, "Server Private Key : %s" % self.keyPrivate)
		self.output(h, "Starting Server with IP %s on Port %s" % (self.ip, self.port))
		
		self.output(h, "Building Socket")
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		self.output(h, "Binding IP and Port")
		self.socket.bind((self.ip, self.port))
		
		self.socket.listen(16)
		self.isOnline = True
		
		Thread(target=self.handlerConnect).start()
		Thread(target=self.handlerSend).start()
		
		self.output(h, "Server Initialised.")
		
	def handshake(self, c):
		h = "Handshaker"
		self.send(Message("H", "SERV", "NEWC", "\n".join([self.keyPublic, self.name]), False))
		self.output(h, "Waiting for Public Key from Client")
		while c.keyPublic == None:
			pass
		while c.name == "Username":
			pass
		self.output(h, "Handshake Complete")
		self.output(h, "Client Public Key: %s" % c.keyPublic)
		self.output(h, "Client Name: %s" % c.name)
		
	def handlerConnect(self):
		h = "Connection"
		while self.isOnline == True:
			self.output(h, "Waiting for Client Connection")
			connection, address = self.socket.accept()
			self.output(h, "New Client Accepted from %s" % str(address[0]))
			c = Client("NEWC", connection, address, self)
			self.clients["NEWC"] = c
			Thread(target=self.handlerClient, args=(c, )).start()
			self.handshake(c)
			self.clients[c.refID] = c
			self.clients.pop("NEWC")
			self.send(Message("C", "SERV", "ALLC", "+%s%s" % (c.refID, c.name), True))
			self.output(h, "Client %s Added Successfully" % c.refID)
			for key, client in self.clients.items():
				if client.refID != c.refID:
					self.send(Message("C", "SERV", c.refID, "+%s%s" % (client.refID, client.name), True))
					
	def handlerSend(self):
		h = "Sender"
		while self.isOnline == True:
			if len(self.queue) > 0:
				m = self.queue.pop(0)
				self.output(h, "Sending Message: %s" % m.data)
				if m.recipient == "ALLC":
					recipients = list(self.clients.values())
				else:
					recipients = [self.clients[m.recipient]]
				for client in recipients:
					try:
						encrypted = self.encrypt(m, (m.encrypt, client.keyPublic))
						client.connection.send(encrypted)
						self.output(h, "Message Sent to %s" % client.refID)
					except ConnectionResetError:
						self.output(h, "Error - %s is No Longer Connected." % client.refID)
						
	def handlerClient(self, client):
		h = "Client Handler (%s)" % client.refID
		self.output(h, "Client Thread Started for Client %s" % client.refID)
		client.isOnline = True
		while self.isOnline == True and client.isOnline == True:
			try:
				encrypted = client.connection.recv(self.maxBytes)
				m = self.decrypt(encrypted, (True, self.keyPrivate))
				if m.mode == "H": #Handshake
					if client.keyPublic == None:
						client.keyPublic, client.refID = m.data, m.sender
					else:
						client.name = m.data

				elif m.mode == "M": #Message
					if m.recipient == "ALLC":
						for key in self.clients:
							self.send(Message("M", m.sender, key, m.data, True))
					else:
						self.send(m)

				elif m.mode == "C": #Client Connect/Disconnect
					for key in self.clients:
						self.send(Message("C", m.sender, key, m.data))

				elif m.mode == "P": #Ping Request
					self.send(Message("P", "SERV", m.sender, m.data, True))

				elif m.mode == "T": #Client is Typing
					#Notify all clients that this client is typing
					pass
			except ConnectionResetError:
				self.output(h, "Client Disconnected, Closing Thread.")
				self.send(Message("C", "SERV", "ALLC", "-%s" % client.refID, True))
				self.clients.pop(client.refID)
				client.isOnline = False
				
	def encrypt(self, m, RSA):
		m = m.construct()
		if RSA[0] == True:
			m = self.rsa.encrypt(m, RSA[1])
		m += "|"
		return m.encode()
		
	def decrypt(self, m, RSA):
		m = m.decode()
		if RSA[0] == True:
			m = self.rsa.decrypt(m, RSA[1])
		return Message(m[0], m[1:5], m[5:9], m[9:], True)
		
	def send(self, m):
		self.queue.append(m)
		
	def output(self, handler, message):
		print("[%s]: %s" % (handler, message))

