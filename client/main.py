import sys
import random
from handler import ServerHandler
from gui import Interface
from aes import AES
from rsa import RSA
from classes import Client

class Main():
    def __init__(self):
        clientRefID = str(random.randint(1000, 9999))
        clientName = str(input("Choose a Username: "))
        self.appClient  = Client(clientRefID, clientName)
        self.appUI      = Interface(self)
        self.appHandler = ServerHandler(self)
        self.appAES     = AES()
        self.appRSA     = RSA()

    def Start(self):
        self.clientKeyPublic, self.clientKeyPrivate = self.appRSA.KeyGen()
        self.appUI.GenerateInterface()
        self.appHandler.LoadServers()
        self.appUI.Master.mainloop()
        self.appHandler.SaveServers()
        sys.exit()
        
App = Main()
App.Start()
