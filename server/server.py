import socket
import datetime
import time
from classes import *
from threading import Thread
from rsa import RSA

class Server():
    def __init__(self, serverIP, serverPort, serverName="Server"):
        self.serverIP           = serverIP
        self.serverPort         = serverPort
        self.serverName         = serverName
        self.serverClients      = {}
        self.serverMessageLog   = []
        self.serverMessageQueue = []
        self.serverRSA          = RSA()
        self.serverMaxBytes     = 8192
        self.serverIsOnline     = False
        self.serverKeyPublic    = None
        self.serverKeyPrivate   = None

    def Start(self):
        h = "Startup"
        self.Output(h, "Generating Public/Private Key")
        self.serverKeyPublic, self.serverKeyPrivate = self.serverRSA.KeyGen()
        self.Output(h, "Server Public Key  : %s" % self.serverKeyPublic)
        self.Output(h, "Server Private Key : %s" % self.serverKeyPrivate)
        self.Output(h, "Starting Server with IP %s on Port %s" % (self.serverIP, self.serverPort))
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Output(h, "Building Socket")
        self.serverSocket.bind((self.serverIP, self.serverPort))
        self.Output(h, "Binding IP and Port")
        self.serverSocket.listen(16)
        self.serverIsOnline = True
        self.Output(h, "Server Initialised.")
        Thread(target=self.ConnectHandler).start()
        Thread(target=self.SendHandler).start()
        
        
    def Handshake(self, clientNew):
        h = "Handshaker"
        self.Send(Message("H", "SERV", "NEWC", "\n".join([self.serverKeyPublic, self.serverName]), False))
        self.Output(h, "Waiting for Public Key from Client")
        while clientNew.clientKeyPublic == None:
            pass
        while clientNew.clientName == "Username":
            pass
        self.Output(h, "Handshake Complete")
        self.Output(h, "Client Public Key: %s" % clientNew.clientKeyPublic)
        self.Output(h, "Client Name: %s" % clientNew.clientName)

    def ConnectHandler(self):
        h = "Connection"
        while self.serverIsOnline == True:
            self.Output(h, "Waiting for Client Connection")
            clientConnection, clientAddress = self.serverSocket.accept()
            self.Output(h, "New Client Accepted from %s" % str(clientAddress[0]))
            clientNew = Client("NEWC", clientConnection, clientAddress, self)
            self.serverClients["NEWC"] = clientNew
            Thread(target=self.ClientHandler, args=(clientNew, )).start()
            self.Handshake(clientNew)
            self.serverClients[clientNew.clientRefID] = clientNew
            self.serverClients.pop("NEWC")
            self.Send(Message("C", "SERV", "ALLC", "+%s%s" % (clientNew.clientRefID, clientNew.clientName), True))
            self.Output(h, "Client %s Added Successfully" % clientNew.clientRefID)
            for key, client in self.serverClients.items():
                print(client.clientRefID)
                if client.clientRefID != clientNew.clientRefID:
                    self.Send(Message("C", "SERV", clientNew.clientRefID, "+%s%s" % (client.clientRefID,
                                                                                         client.clientName), True))
            
    def SendHandler(self):
        h = "Sender"
        while self.serverIsOnline == True:
            if len(self.serverMessageQueue) > 0:
                serverMessageCache = self.serverMessageQueue.pop(0)
                print(serverMessageCache)
                self.Output(h, "Sending Message: %s" % serverMessageCache.messageData)
                if serverMessageCache.messageRecipient == "ALLC":
                    messageRecipients = list(self.serverClients.values())
                else:
                    messageRecipients = [self.serverClients[serverMessageCache.messageRecipient]]
                for client in messageRecipients:
                    try:
                        print("MESSAGE: %s" % serverMessageCache.messageData)
                        messageEncrypted = self.Encrypt(serverMessageCache,
                                                        (serverMessageCache.messageEncrypt, client.clientKeyPublic))
                        client.clientConnection.send(messageEncrypted)
                        self.Output(h, "Message Sent to %s" % client.clientRefID)
                    except ConnectionResetError:
                        self.Output(h, "Error - %s is No Longer Connected." % client.clientRefID)

    def ClientHandler(self, client):
        h = "Client Handler (%s)" % client.clientRefID
        self.Output(h, "Client Thread Started for Client %s" % client.clientRefID)
        clientIsOnline = True
        while self.serverIsOnline == True and clientIsOnline == True:
            try:
                messageEncrypted = client.clientConnection.recv(self.serverMaxBytes)
                messageObject    = self.Decrypt(messageEncrypted, (True, self.serverKeyPrivate))

                if messageObject.messageType   == "H": #Handshake
                    if client.clientKeyPublic == None:
                        client.clientKeyPublic, client.clientRefID = messageObject.messageData, messageObject.messageSender
                    else:
                        client.clientName = messageObject.messageData

                elif messageObject.messageType == "M": #Message
                    if messageObject.messageRecipient == "ALLC":
                        for key in self.serverClients:
                            self.Send(Message("M", messageObject.messageSender,
                                              key, messageObject.messageData, True))
                    else:
                        self.Send(messageObject)

                elif messageObject.messageType == "C": #Client Connect/Disconnect
                    for key in self.serverClients:
                        self.Send(Message("C", messageObject.messageSender,
                                          key, messageObject.messageData))

                elif messageObject.messageType == "P": #Ping Request
                    self.Send(Message("P", "SERV", messageObject.messageSender,
                                      messageObject.messageData, True))
                    pass

                elif messageObject.messageType == "T": #Client is Typing
                    #Notify all clients that this client is typing
                    pass
            except ConnectionResetError:
                self.Output(h, "Client Disconnected, Closing Thread.")
                self.Send(Message("C", "SERV", "ALLC", "-%s" % client.clientRefID, True))
                self.serverClients.pop(client.clientRefID)
                clientIsOnline = False
                
    def Encrypt(self, messageObject, RSA):
        messageText = messageObject.Construct()
        if RSA[0] == True:
            messageText = self.serverRSA.Encrypt(messageText, RSA[1])
        messageText += "|"
        messageText = messageText.encode()
        return messageText

    def Decrypt(self, messageText, RSA):
        messageText = messageText.decode()
        if RSA[0] == True:
            messageText = self.serverRSA.Decrypt(messageText, RSA[1])
        messageObject = Message(messageText[0], messageText[1:5], messageText[5:9], messageText[9:], True)
        return messageObject
    
    def Send(self, messageObject):
        self.serverMessageQueue.append(messageObject)

    def Output(self, handler, message):
        print("[%s]: %s" % (handler, message))
        pass
        
    
        
        
