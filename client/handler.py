from threading import Thread
from server import Server
from gui import *

class ServerHandler():
	def __init__(self, app):
		self.app           = app
		self.servers       = []
		self.count         = 0
		self.currentServer = None
		self.isFirstRun    = True
		
	def loadServers(self):
		open("servers.txt", "a").close()
		f = open("servers.txt", "r")
		servers = f.read().split("\n")[:-1]
		for i in servers:
			ip, port = i.split(":")
			self.addServer(ip, port)
		f.close()
		
	def saveServers(self):
		f = open("servers.txt", "w")
		for i in self.servers:
			data = "%s:%s\n" % (i.ip, i.port)
			f.write(data)
		f.close()
		
	def checkAddress(self, ip, port):
		numDots = 0
		if ip != "localhost":
			for i in range(len(ip)):
				if ip[i] not in [".", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
					return "Not an IP Address!"
				if ip[i] == ".":
					numDots += 1
			if numDots != 3:
				return "Bad IP!"
			for i in ip.split("."):
				if i == "":
					return "Bad IP!"
				elif int(i) > 255:
					return "Bad IP!"
		if port.isdigit() and int(port) > 255:
			return True
		else:
			return "Bad Port!"
			
	def changeServer(self, num):
		print("Changing Server")
		self.app.ui.clear(["Input", "Output"])
		self.app.ui.sendButton.configure(state='disabled')
		self.app.ui.chatboxInput.configure(state='disabled')
		if self.isFirstRun == False:
			self.app.ui.clear(["Clients"])
			self.currentServer.isCurrentServer = False
		else:
			self.isFirstRun = False
			
		self.currentServer = self.servers[num]
		self.currentServer.isCurrentServer = True
		
		if self.currentServer.isOnline == True:
			for key, client in self.currentServer.clients.items():
				client.clientFrame = self.app.ui.createClientFrame(client, len(self.currentServer.clients))
			for message in self.currentServer.log:
				self.app.ui.displayMessage(message, self.currentServer.clients[message.sender].name)
			self.app.ui.serverNameLabel.configure(text=self.currentServer.name)
			self.app.ui.chatboxInput.configure(state='normal')
			self.app.ui.sendButton.configure(state='normal')
			
	def addServer(self, IP, Port):
		check = self.checkAddress(IP, Port)
		if check == True:
			newServer = Server(self.app, IP, int(Port), self.count)
			if newServer not in self.servers:
				try:
					newServer.button = self.app.ui.createServerButton(newServer.num, "Connecting...")
					self.servers.append(newServer)
					self.count += 1
					Thread(target=newServer.connect, daemon=True).start()
				except:
					print("Error")
			else:
				self.app.ui.displayError("Error", "Server Already Added!")
		else:
			self.app.ui.displayError("Error", check)
			
	def removeServer(self, num):
		self.servers.replace(self.servers[num], None)
