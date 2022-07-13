from threading import Thread
from server import Server
from gui import *

class ServerHandler():
    def __init__(self, appMain):
        self.appMain                  = appMain
        self.handlerServerList        = []
        self.handlerServerNum         = 0
        self.handlerCurrentServer     = None
        self.handlerIsFirstRun        = True

    def LoadServers(self):
            open("servers.txt", "a").close()
            f = open("servers.txt", "r")
            servers = f.read().split("\n")[:-1]
            for i in servers:
                ip, port = i.split(":")
                self.AddServer(ip, port)
            f.close()

    def SaveServers(self):
            f = open("servers.txt", "w")
            for i in self.handlerServerList:
                data = "%s:%s\n" % (i.serverIP, i.serverPort)
                f.write(data)
            f.close() 

    def CheckAddress(self, ip, port):
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
        if port.isdigit() == False and port > 0 and port < 255:
            return "Bad Port!"
        else:
            return True
        
        
    def ChangeServer(self, serverNum):
        print("Changing Server")
        self.appMain.appUI.Clear(["Input", "Output"])
        self.appMain.appUI.SendButton.configure(state='disabled')
        self.appMain.appUI.ChatboxInput.configure(state='disabled')
        if self.handlerIsFirstRun == False:
            self.appMain.appUI.Clear(["Clients"])
            self.handlerCurrentServer.serverIsCurrentServer = False
        else:
            self.handlerIsFirstRun = False

        self.handlerCurrentServer = self.handlerServerList[serverNum]
        self.handlerCurrentServer.serverIsCurrentServer = True

        if self.handlerCurrentServer.serverIsOnline == True:
            for key, client in self.handlerCurrentServer.serverClients.items():
                client.clientFrame = self.appMain.appUI.CreateClientFrame(client, len(self.handlerCurrentServer.serverClients))
            for message in self.handlerCurrentServer.serverMessageLog:
                self.appMain.appUI.DisplayMessage(message,
                                                  self.handlerCurrentServer.serverClients[message.messageSender].clientName)
            self.appMain.appUI.ServerNameLabel.configure(text=self.handlerCurrentServer.serverName)
            self.appMain.appUI.ChatboxInput.configure(state='normal')
            self.appMain.appUI.SendButton.configure(state='normal')
        
    def AddServer(self, IP, Port):
        check = self.CheckAddress(IP, Port)
        if check == True:
            newServer = Server(IP, int(Port), self.handlerServerNum, self.appMain)
            if newServer not in self.handlerServerList:
                try:
                    newServer.serverButton = self.appMain.appUI.CreateServerButton(newServer.serverNum,
                                                                                   "Connecting...")
                    self.handlerServerList.append(newServer)
                    self.handlerServerNum += 1
                    Thread(target=newServer.Connect, daemon=True).start()
                except:
                    print("Error")
            else:
                self.appMain.appUI.DisplayError("Error", "Server Already Added!")
        else:
            self.appMain.appUI.DisplayError("Error", check)
    def RemoveServer(self, serverNum):
        self.handlerServerList.replace(self.handlerServerList[serverNum], None)
