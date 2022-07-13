from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import time

#PARAMETER ORDER : (parent, width, height, text, command, fg, bg, bd, relief, state)
#GRID ORDER      : (row, column, padx, pady, rowspan, columnspan, sticky)

class Interface():
    def __init__(self, appMain):
        self.appMain = appMain
        self.Master = Tk()
        self.Master.title("Chatroom")
        self.Master.protocol("WM_DELETE_WINDOW", self.OnClose)
        self.Master.resizable(0,0)
        self.BackgroundColour       = "azure"
        self.ButtonColour           = "slate gray"
        self.WidgetBackgroundColour = "gainsboro"
        self.WindowOpen = False
        self.Master.configure(bg=self.BackgroundColour)    
        
    def OnClose(self):
        if messagebox.askokcancel("Quit?", "Do You Want to Quit?") == True:
            self.Master.destroy()
        
    def GenerateInterface(self):
        self.GenerateFrames()
        self.GenerateTopLeft()
        self.GenerateTopMiddle()
        self.GenerateTopRight()
        self.GenerateBottomLeft()
        self.GenerateBottomMiddle()
        self.GenerateBottomRight()

    def GenerateFrames(self):
        self.TopRight     = Frame(self.Master, width=30,  height=16,  bg=self.BackgroundColour)
        self.TopMiddle    = Frame(self.Master, width=690, height=480, bg=self.BackgroundColour)
        self.TopLeft      = Frame(self.Master, width=30,  height=16,  bg=self.BackgroundColour)
        self.BottomRight  = Frame(self.Master, width=30,  height=4,   bg=self.BackgroundColour)
        self.BottomMiddle = Frame(self.Master, width=100, height=4,   bg=self.BackgroundColour)
        self.BottomLeft   = Frame(self.Master, width=30,  height=4,   bg=self.BackgroundColour)

        self.TopLeft.grid(      row=0, column=0, pady=(5,5), padx=5)
        self.TopMiddle.grid(    row=0, column=1, pady=(5,5), padx=0)
        self.TopRight.grid(     row=0, column=2, pady=(5,5), padx=5)
        self.BottomLeft.grid(   row=1, column=0, pady=(0,5), padx=5)
        self.BottomMiddle.grid( row=1, column=1, pady=(0,5), padx=0)
        self.BottomRight.grid(  row=1, column=2, pady=(0,5), padx=5)
        
    def GenerateTopLeft(self):
        self.ServerLabel       = Label(self.TopLeft, text="Servers:", bg=self.BackgroundColour)
        self.ServerScrollFrame = ScrollFrame(self.TopLeft, width=128, height=480, bg=self.WidgetBackgroundColour)

        self.ServerLabel.grid(row=0, column=0)
        self.ServerScrollFrame.grid(row=1, column=0, padx=0)
        
    def GenerateTopMiddle(self):
        self.ServerNameLabel  = Label(self.TopMiddle, text="Server: None", bg=self.BackgroundColour)
        self.ServerUsersLabel = Label(self.TopMiddle, text="Number of Users Online:", bg=self.BackgroundColour)
        self.ChatboxText      = ScrollFrame(self.TopMiddle, width=690, height=440, bg=self.WidgetBackgroundColour)
        
        self.ServerNameLabel.grid(row=0, column=0, sticky=W)
        self.ServerUsersLabel.grid(row=0, column=1, sticky=E)
        self.ChatboxText.grid(row=1, column=0, columnspan=2)
        
    def GenerateTopRight(self):
        self.UserLabel        = Label(self.TopRight, text="Users:", bg=self.BackgroundColour)
        self.UsersScrollFrame = ScrollFrame(self.TopRight, width=128, height=480, bg=self.WidgetBackgroundColour)

        self.UserLabel.grid(row=0, column=0)
        self.UsersScrollFrame.grid(row=2, column=0, padx=0)
        
    def GenerateBottomLeft(self):
        self.AddServerButton  = Button(self.BottomLeft,
        width=20, height=2, text="Add Server", relief=GROOVE, bg=self.ButtonColour,
        command=lambda:self.CreateWindow("Add Server"))

        self.PingLabel        = Label(self.BottomLeft,
        width=10, height=2, text="Ping: n/a ms", fg="red", bg=self.BackgroundColour)
        
        self.AddServerButton.grid(row=0, column=0, pady=(0, 0))
        self.PingLabel.grid(row=1, column=0)
        
    def GenerateBottomMiddle(self):
        self.ChatboxInput = Text(self.BottomMiddle,
        width=90, height=5, wrap=WORD, relief=GROOVE,
        state=DISABLED, font=("Helvetica", 9), bg=self.WidgetBackgroundColour)

        self.SendButton   = Button(self.BottomMiddle,
        width=10, height=5, text="Send", relief=GROOVE, bg=self.ButtonColour,
        command=lambda:self.SendMessage("Click"), state=DISABLED)

        self.Master.bind('<Return>', lambda x:self.SendMessage("Return"))
        
        self.ChatboxInput.grid(row=1, column=0, rowspan=2)
        self.SendButton.grid(row=1, column=1)
        
    def GenerateBottomRight(self):
        self.UsernameSetAsLabel = Label(self.BottomRight,
        text="Your Username:", bg=self.BackgroundColour)
        
        self.UsernameLabel      = Label(self.BottomRight,
        text=self.appMain.appClient.clientName, bg=self.BackgroundColour)

        self.UsernameSetAsLabel.grid(row=0)
        self.UsernameLabel.grid(row=1)
        
    def SendMessage(self, event):
        raw = self.ChatboxInput.get('1.0', END)
        if event == "Return":
            raw = raw[:-2]
        self.appMain.appHandler.handlerCurrentServer.Send("M", self.appMain.appClient.clientRefID, "ALLC", raw, True)

    def DisplayMessage(self, messageObject, senderName):
        m = MessageBox(self.ChatboxText.innerFrame, messageObject.messageData, senderName)
        m.grid(column=0)
        self.ChatboxText.canvas.configure(scrollregion=self.ChatboxText.canvas.bbox("all"))
        self.ChatboxText.canvas.yview_moveto(1)
        self.ChatboxText.scrollbar.update()
        self.ChatboxText.update()
        self.ChatboxText.innerFrame.update()

    def DisplayError(self, errortitle, errormessage):
        messagebox.showerror(errortitle, errormessage)

    def CreateWindow(self, windowtype):
        if self.WindowOpen == False:
            self.WindowOpen = True
            NewWindow = Window(self, windowtype)
            NewWindow.grid()

    def CreateServerButton(self, serverNum, serverName):
        serverButton = ServerButton(self.ServerScrollFrame.innerFrame, serverNum, serverName,
                                    command=lambda:self.appMain.appHandler.ChangeServer(serverNum),
                                    bg=self.ButtonColour)
        serverButton.grid()
        return serverButton
        
    def Clear(self, boxes):
        if "Input" in boxes:
            self.ChatboxInput.delete('1.0', END)
        if "Output" in boxes:
            self.ChatboxText.destroy()
            self.ChatboxText = ScrollFrame(self.TopMiddle, width=690, height=440, bg=self.WidgetBackgroundColour)
            self.ChatboxText.grid(row=1, column=0, columnspan=2)
        if "Clients" in boxes:
            self.UsersScrollFrame.destroy()
            self.UsersScrollFrame = ScrollFrame(self.TopRight, width=128, height=480, bg=self.WidgetBackgroundColour)
            self.UsersScrollFrame.grid(row=2, column=0, padx=0)
        
    def CreateClientFrame(self, client, count):
        clientFrame = Label(self.UsersScrollFrame.innerFrame, width=14, height=1,
                            text=client.clientName, bg=self.WidgetBackgroundColour)

        clientFrame.grid(column=0)
        self.ServerUsersLabel.configure(text="%s User(s) Online" % count)
        return clientFrame

    def RemoveClientFrame(self, clientFrame, count):
        clientFrame.destroy()
        self.ServerUsersLabel.configure(text="%s User(s) Online" % count)

class Window(Toplevel):
    def __init__(self, interface, windowtype, data="", *args, **kwargs):
        Toplevel.__init__(self, interface.Master)
        self.interface = interface
        self.windowtype = windowtype
        self.title(windowtype)
        self.protocol("WM_DELETE_WINDOW", self.Close)
        
        self.top = Frame(self)
        self.bottom = Frame(self)
        
        self.acceptButton = Button(self.bottom, width=10, height=1, text="OK", relief=GROOVE,
                                   command=lambda:self.RunCommand())

        self.cancelButton = Button(self.bottom, width=10, height=1, text="Cancel", relief=GROOVE,
                                   command=self.Close)

        self.top.grid(row=0, column=0)
        self.bottom.grid(row=1, column=0)
        self.acceptButton.grid(row=0, column=1, padx=10, pady=10)
        self.cancelButton.grid(row=0, column=0, padx=10, pady=10)

        if windowtype == "Add Server":
            self.ipEntry   = Entry(self.top, width=30)
            self.ipLabel   = Label(self.top, width=15, text="IP Address:", anchor="e")
            self.portEntry = Entry(self.top, width=30)
            self.portLabel = Label(self.top, width=15, text="Port:", anchor="e")

            self.ipEntry.grid(row=0, column=1)
            self.ipLabel.grid(row=0, column=0)
            self.portEntry.grid(row=1, column=1)
            self.portLabel.grid(row=1, column=0)

        elif windowtype == "Error":
            self.errorLabel = Label(self.top, width=20, text=data)
            self.cancelButton.destroy()
            self.errorLabel.grid(row=0, column=0)

    def RunCommand(self):
        if self.windowtype == "Log In":
            pass

        elif self.windowtype == "Sign Up":
            pass
        
        elif self.windowtype == "Add Server":
            self.interface.appMain.appHandler.AddServer(self.ipEntry.get(), self.portEntry.get())

        self.Close()

    def Close(self):
        self.interface.WindowOpen = False
        self.destroy()

class ScrollFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, relief=GROOVE, bd=1, *args, **kwargs)
        self.w = kwargs['width']
        self.h = kwargs['height']
        self.canvas = Canvas(self, width=self.w, height=self.h, bg=self.cget('bg'),
                             highlightbackground=self.cget('bg'))

        self.innerFrame = Frame(self.canvas, width=self.w, bg=self.cget('bg'),
                                highlightbackground=self.cget('bg'))

        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                   relief=GROOVE, bg="red", highlightbackground=self.cget('bg'))

        self.canvas.grid(row=0, column=0)
        self.innerFrame.grid(row=0, column=0)
        self.scrollbar.grid(row=0, column=1, sticky=N+S)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0,0), window=self.innerFrame, anchor="nw")
##        self.canvas.bind("<Configure>", self.Scroll)

##    def Scroll(self, event):
##        self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=self.w, height=self.h)

class ServerButton(Frame):
    def __init__(self, parent, serverNum, serverName, *args, **kwargs):
        Frame.__init__(self, parent, bg=parent.cget('bg'))
        self.serverName = serverName
        self.serverNum  = serverNum
        self.serverStatus = Button(self, width=1, height=1, bg="red", relief=FLAT, state=DISABLED)
        self.serverButton = Button(self, text=self.serverName, width=14, height=1, relief=GROOVE,
                                   state=DISABLED, *args, **kwargs)

        self.serverStatus.grid(row=0, column=0, padx=1, pady=2)
        self.serverButton.grid(row=0, column=1)

##class UserButton(Frame):
##    def __init__(self, parent, userName):
##        Frame.__init__(self, parent, text=userName, width=14, height=2)
##        self.userName = userName

class MessageBox(Frame):
    def __init__(self, parent, messageData, messageSender, *args, **kwargs):
        Frame.__init__(self, parent, bg=parent.cget('bg'))
        self.messageSender = Label(self, text=messageSender, height=1,
                                   font=("Helvetica", "9", "bold"), bg=self.cget('bg'))

        self.messageText = Label(self, width=98, height=round((len(messageData)/98)+0.5),
                                 font=("Helvetica", 9), text=messageData, relief=FLAT,
                                 wraplength=690, anchor=NW, justify=LEFT, bg=self.cget('bg'))

        self.messageSeparator = Frame(self, height=2, bd=1, relief=SUNKEN,
                                      highlightbackground=self.cget('bg'), bg=self.cget('bg'))

        self.messageSender.grid(row=0, column=0, sticky=N+W)
        self.messageText.grid(row=1, column=0, sticky=N+W)
        self.messageSeparator.grid(row=2, column=0, sticky=E+W, pady=5, padx=2)
