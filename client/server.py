from threading import Thread
import socket
import time
from classes import *
from rsa import RSA
from aes import AES
import traceback

class Server():
    def __init__(self, serverIP, serverPort, serverNum, appMain, serverName="Server"):
        self.appMain               = appMain
        self.serverIP              = serverIP
        self.serverPort            = serverPort
        self.serverName            = serverName
        self.serverNum             = serverNum
        self.serverClients         = {}
        self.serverMessageLog      = []
        self.serverMessageQueue    = []
        self.serverRSA             = RSA()
        self.serverAES             = AES()
        self.serverMaxBytes        = 8192
        self.serverButton          = None
        self.serverIsOnline        = False
        self.serverIsCurrentServer = False
        self.serverKeyPublic       = None
        self.clientKeyPublic       = appMain.clientKeyPublic
        self.clientKeyPrivate      = appMain.clientKeyPrivate
        self.clientRefID           = appMain.appClient.clientRefID
        self.clientIsTyping        = False
    def __eq__(self, other):
        return (self.serverIP == other.serverIP and self.serverPort == other.serverPort)
        
    def Connect(self):
        h = "Connection"
        while self.serverIsOnline == False:
            try:
                self.Output(h, "Client Public Key  : %s" % self.clientKeyPublic)
                self.Output(h, "Client Private Key : %s" % self.clientKeyPrivate)
                self.Output(h, "Connecting to Server")
                self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.clientSocket.connect((self.serverIP, self.serverPort))
                self.serverIsOnline = True
                self.serverButton.serverStatus.configure(bg="green")
                self.Output(h, "Connected to Server.")
                Thread(target=self.Recieve, daemon=True).start()
                self.Handshake()
                self.serverButton.serverButton.configure(state='normal')
                Thread(target=self.Ping, daemon=True).start()
            except Exception as E:
                self.clientSocket.close()
                self.Output(h, "Could Not Connect. Retrying in 5 Seconds...")
                time.sleep(5)
    
    def Disconnect(self):
        self.clientSocket.close()
        self.serverIsOnline = False
        self.serverButton.serverStatus.configure(bg="red")
        self.serverKeyPublic = None
        if self.serverIsCurrentServer == True:
            for key, i in self.serverClients.items():
                self.appMain.appUI.RemoveClientFrame(i.clientFrame)
        self.serverClients = {}
        self.appMain.appHandler.handlerCurrentServer.serverButton.configure(state='disabled')
        self.appMain.appHandler.ChangeServer(-1)
        
    def Handshake(self):
        h = "Handshaker"
        self.Output(h, "Waiting for Public Key from Server")
        while self.serverKeyPublic == None:
            pass
        
        self.Send("H", self.clientRefID, "SERV", self.clientKeyPublic, True)
        self.Send("H", self.clientRefID, "SERV", self.appMain.appClient.clientName, True)
        self.Output(h, "Handshake Complete.")
    
    def Check(self, message):
        characters = list(message)
        messageOK = False
        for i in characters:
            if i not in [" ", "", "\n"]:
                messageOK = True
        return messageOK
    
    def Ping(self):
        h = "Ping"
        while self.serverIsOnline == True:
            self.startTime = time.time()
            self.Output(h, "Pinging Server")
            self.Send("P", self.clientRefID, "SERV", "Ping", True)
            time.sleep(7)
    
    def Send(self, messageType, messageSender, messageRecipient, messageData, messageEncrypt):
        h = "Sender"
        messageObject = Message(messageType, messageSender, messageRecipient, messageData[:512], messageEncrypt)
        if messageObject.messageType == "M":
            self.appMain.appUI.Clear(["Input"])
        self.Output(h, "Sending Message")
        serverMessageCache = messageObject
        if self.Check(serverMessageCache.messageData) == True:
            messageEncrypted = self.Encrypt(serverMessageCache, (serverMessageCache.messageEncrypt,
                                                                 self.serverKeyPublic))

            if serverMessageCache.messageRecipient in ["SERV", "ALLC"]:
                self.clientSocket.send(messageEncrypted)
            else:
                pass
            self.Output(h, "Message Sent.")
            
##    def SendHandler(self):
##        time.sleep(0.1)
##        h = "Sender"
##        while self.serverIsOnline == True:
##            if len(self.serverMessageQueue) > 0:
##                self.Output(h, "Sending Message")
##                serverMessageCache = self.serverMessageQueue.pop(0)
##                if self.Check(serverMessageCache.messageData) == True:
##                    messageEncrypted = self.Encrypt(serverMessageCache, (serverMessageCache.messageEncrypt, self.serverKeyPublic))
##                    if serverMessageCache.messageRecipient in ["SERV", "ALLC"]:
##                        self.clientSocket.send(messageEncrypted)
##                    else:
##                        pass
##                    self.Output(h, "Message Sent.")

    def Recieve(self):
        h = "Reciever"
        handshakeRecieved = False
        while self.serverIsOnline == True:
            try:
                fullMessageReceived = False
                messageEncrypted = b''
                while fullMessageReceived == False:
                    messageEncrypted += self.clientSocket.recv(1)
                    if messageEncrypted.decode()[-1] == "|":
                        fullMessageReceived = True
                        print(messageEncrypted.decode())
                        messageEncrypted = messageEncrypted[:-1]

                #messageEncrypted = self.clientSocket.recv(self.serverMaxBytes)
                if handshakeRecieved == False:
                    messageObject = self.Decrypt(messageEncrypted, (False, None))
                    handshakeRecieved = True
                else:
                    messageObject = self.Decrypt(messageEncrypted, (True, self.clientKeyPrivate))
                if messageObject.messageType == "H":
                    self.serverKeyPublic, self.serverName = messageObject.messageData.split("\n")
                    self.Output(h, "Server Public Key: %s" % self.serverKeyPublic)
                    self.Output(h, "Server Name: %s" % self.serverName)
                    self.serverButton.serverButton.configure(text=self.serverName)

                elif messageObject.messageType == "M": #Message
                    self.serverMessageLog.append(messageObject)
                    if self.serverIsCurrentServer == True:
                        self.appMain.appUI.DisplayMessage(messageObject, self.serverClients[messageObject.messageSender].clientName)

                elif messageObject.messageType == "C": #Client Connect/Disconnect
                    
                    if messageObject.messageData[0] == "+":
                        print(self.serverClients)
                        print("Name: %s" % messageObject.messageData[5:])
                        self.serverClients[messageObject.messageData[1:5]] = Client(messageObject.messageData[1:5], messageObject.messageData[5:])
                        if self.serverIsCurrentServer == True:
                            self.serverClients[messageObject.messageData[1:5]].clientFrame = self.appMain.appUI.CreateClientFrame(self.serverClients[messageObject.messageData[1:5]], len(self.serverClients))
                            print("Made a client frame")
                    elif messageObject.messageData[0] == "-":
                        print(self.serverClients)
                        if self.serverIsCurrentServer == True:
                            self.appMain.appUI.RemoveClientFrame(self.serverClients[messageObject.messageData[1:5]].clientFrame, len(self.serverClients)-1)
                        self.serverClients.pop(messageObject.messageData[1:5])
                    pass

                elif messageObject.messageType == "P":
                    self.pingTime = int((time.time()-self.startTime)*100)
                    if self.pingTime < 50:
                        colour = "GREEN"
                    elif self.pingTime < 100:
                        colour = "ORANGE"
                    else:
                        colour = "RED"
                    if self.serverIsCurrentServer == True:
                        self.appMain.appUI.PingLabel.configure(text=("Ping: %s ms" % self.pingTime), fg=colour)
                
            except:
                self.Output(h, "Server Offline, Attempting to Reconnect...")
                self.Disconnect()
                self.Connect()

    def Encrypt(self, messageObject, RSA):
        if messageObject.messageType in ["M","P"]:
            messageObject.messageData = self.serverAES.Encrypt(messageObject.messageData)
        messageText = messageObject.Construct()
        if RSA[0] == True:
            messageText = self.serverRSA.Encrypt(messageText, RSA[1])
        messageText = messageText.encode()
        return messageText

    def Decrypt(self, messageText, RSA):
        messageText = messageText.decode()
        if RSA[0] == True:
            messageText = self.serverRSA.Decrypt(messageText, RSA[1])
        print("Raw String: %s" % messageText)
        messageObject = Message(messageText[0], messageText[1:5], messageText[5:9], messageText[9:], True)
        print(messageObject.messageData)
        if messageObject.messageType in ["M","P"]:
            messageObject.messageData = self.serverAES.Decrypt(messageObject.messageData)
        return messageObject

    def Output(self, handler, message):
##        print("[%s]: %s" % (handler, message))
        pass

