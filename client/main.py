import sys
import random
from handler import ServerHandler
from gui import Interface
from aes import AES
from rsa import RSA
from classes import Client

class Main():
	def __init__(self):
		refID        = str(random.randint(1000, 9999))
		name         = str(input("Choose a Username: "))
		self.client	 = Client(refID, name)
		self.ui		 = Interface(self)
		self.handler = ServerHandler(self)
		self.aes	 = AES()
		self.rsa	 = RSA()

	def Start(self):
		self.keyPublicClient, self.keyPrivateClient = self.rsa.KeyGen()
		self.ui.generateInterface()
		self.handler.loadServers()
		self.ui.root.mainloop()
		self.handler.saveServers()
		sys.exit()
		
app = Main()
app.Start()
