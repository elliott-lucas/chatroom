import socket
import datetime
from threading import Thread

class Message():
    def __init__(self, messageType, messageSender, messageRecipient, messageData, messageEncrypt):
        self.messageType      = messageType
        self.messageSender    = messageSender
        self.messageRecipient = messageRecipient
        self.messageData      = messageData
        self.messageUsername  = "Username"
        self.messageEncrypt   = messageEncrypt
    def Construct(self):
        message = "".join([self.messageType,self.messageSender,self.messageRecipient,self.messageData])
        return message

class Client():
    def __init__(self, clientRefID, clientConnection, clientAddress, clientServer, clientKeyPublic=None):
        self.clientName       = "Username"
        self.clientRefID      = clientRefID
        self.clientConnection = clientConnection
        self.clientAddress    = clientAddress
        self.clientIP         = str(clientAddress[0])
        self.clientPort       = str(clientAddress[1])
        self.clientServer     = clientServer
        self.clientKeyPublic  = clientKeyPublic
    def __repr__(self):
        return ("[%s : %s]" % (self.clientName, str(self.clientAddress)))
    def __eq__(self, other):
        return self.clientRefID == other.clientRefID



##def GetUserInfo(userRefID):
##        file = open("Users.csv", "r")
##        table = file.read()
##        record = table.split("\n")[int(userRefID)-1]
##        name = record.split(",")[1]
##        file.close()
##        return name
