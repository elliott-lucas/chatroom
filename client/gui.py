from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import time

# PARAMETER ORDER : (parent, width, height, text, command, fg, bg, bd, relief, state)
#      GRID ORDER : (row, column, padx, pady, rowspan, columnspan, sticky)

BACKGROUND_COLOUR = "azure"
BUTTON_COLOUR     = "slate gray"
WIDGET_COLOUR     = "gainsboro"

class Interface():
	def __init__(self, app):
		self.app          = app
		self.root         = Tk()
		self.isWindowOpen = False
		
		self.root.title("Chatroom")
		self.root.protocol("WM_DELETE_WINDOW", self.onClose)
		self.root.resizable(0,0)
		self.root.configure(bg=BACKGROUND_COLOUR)
		
	def onClose(self):
		if messagebox.askokcancel("Exit App", "Exit?") == True:
			self.app.handler.currentServer.disconnect()
			self.root.destroy()
			
	def generateInterface(self):
		self.generateFrames()
		self.generateTopLeft()
		self.generateTopMiddle()
		self.generateTopRight()
		self.generateBottomLeft()
		self.generateBottomMiddle()
		self.generateBottomRight()
		
	def generateFrames(self):
		self.topLeft	  = Frame(self.root, width=30,  height=16,  bg=BACKGROUND_COLOUR)
		self.topMiddle	  = Frame(self.root, width=690, height=480, bg=BACKGROUND_COLOUR)
		self.topRight	  = Frame(self.root, width=30,  height=16,  bg=BACKGROUND_COLOUR)
		self.bottomLeft	  = Frame(self.root, width=30,  height=4,   bg=BACKGROUND_COLOUR)
		self.bottomMiddle = Frame(self.root, width=100, height=4,   bg=BACKGROUND_COLOUR)
		self.bottomRight  = Frame(self.root, width=30,  height=4,   bg=BACKGROUND_COLOUR)
		
		self.topLeft.grid(row=0, column=0, pady=(5,5), padx=5)
		self.topMiddle.grid(row=0, column=1, pady=(5,5), padx=0)
		self.topRight.grid(row=0, column=2, pady=(5,5), padx=5)
		self.bottomLeft.grid(row=1, column=0, pady=(0,5), padx=5)
		self.bottomMiddle.grid(row=1, column=1, pady=(0,5), padx=0)
		self.bottomRight.grid(row=1, column=2, pady=(0,5), padx=5)
		
	def generateTopLeft(self):
		self.serversLabel       = Label(self.topLeft, text="Servers:", bg=BACKGROUND_COLOUR)
		self.serversScrollFrame = ScrollFrame(self.topLeft, width=128, height=480, bg=WIDGET_COLOUR)

		self.serversLabel.grid(row=0, column=0)
		self.serversScrollFrame.grid(row=1, column=0, padx=0)
		
	def generateTopMiddle(self):
		self.serverNameLabel  = Label(self.topMiddle, text="Server: None", bg=BACKGROUND_COLOUR)
		self.serverUsersLabel = Label(self.topMiddle, text="Number of Users Online:", bg=BACKGROUND_COLOUR)
		self.chatboxText      = ScrollFrame(self.topMiddle, width=690, height=440, bg=WIDGET_COLOUR)
		
		self.serverNameLabel.grid(row=0, column=0, sticky=W)
		self.serverUsersLabel.grid(row=0, column=1, sticky=E)
		self.chatboxText.grid(row=1, column=0, columnspan=2)
		
	def generateTopRight(self):
		self.usersLabel       = Label(self.topRight, text="Users:", bg=BACKGROUND_COLOUR)
		self.usersScrollFrame = ScrollFrame(self.topRight, width=128, height=480, bg=WIDGET_COLOUR)

		self.usersLabel.grid(row=0, column=0)
		self.usersScrollFrame.grid(row=2, column=0, padx=0)
		
	def generateBottomLeft(self):
		self.addServerButton = Button(self.bottomLeft, width=20, height=2, text="Add Server", relief=GROOVE, bg=BUTTON_COLOUR, command=lambda:self.createWindow("Add Server"))
		self.pingLabel       = Label(self.bottomLeft, width=10, height=2, text="Ping: n/a ms", fg="red", bg=BACKGROUND_COLOUR)
		
		self.addServerButton.grid(row=0, column=0, pady=(0, 0))
		self.pingLabel.grid(row=1, column=0)
		
	def generateBottomMiddle(self):
		self.chatboxInput = Text(self.bottomMiddle, width=90, height=5, wrap=WORD, relief=GROOVE, state=DISABLED, font=("Helvetica", 9), bg=WIDGET_COLOUR)
		self.sendButton   = Button(self.bottomMiddle, width=10, height=5, text="Send", relief=GROOVE, bg=BUTTON_COLOUR, command=lambda:self.sendMessage("Click"), state=DISABLED)
		
		self.chatboxInput.grid(row=1, column=0, rowspan=2)
		self.sendButton.grid(row=1, column=1)
		
		self.root.bind('<Return>', lambda x:self.sendMessage("Return"))
		
	def generateBottomRight(self):
		self.usernameSetAsLabel = Label(self.bottomRight, text="Your Username:", bg=BACKGROUND_COLOUR)
		self.usernameLabel      = Label(self.bottomRight, text=self.app.client.name, bg=BACKGROUND_COLOUR)

		self.usernameSetAsLabel.grid(row=0)
		self.usernameLabel.grid(row=1)
		
	def sendMessage(self, event):
		raw = self.chatboxInput.get('1.0', END)
		if event == "Return":
			raw = raw[:-2]
		self.app.handler.currentServer.send("M", self.app.client.refID, "ALLC", raw, True)
		
	def displayMessage(self, messageObject, senderName):
		m = MessageBox(self.chatboxText.innerFrame, messageObject.data, senderName)
		m.grid(column=0)
		self.chatboxText.canvas.configure(scrollregion=self.chatboxText.canvas.bbox("all"))
		self.chatboxText.canvas.yview_moveto(1)
		self.chatboxText.scrollbar.update()
		self.chatboxText.update()
		self.chatboxText.innerFrame.update()
		
	def displayError(self, errortitle, errormessage):
		messagebox.showerror(errortitle, errormessage)
		
	def createWindow(self, windowtype):
		if self.isWindowOpen == False:
			self.isWindowOpen = True
			NewWindow = Window(self, windowtype)
			NewWindow.grid()
			
	def createServerButton(self, num, name):
		button = ServerButton(self.serversScrollFrame.innerFrame, num, name, command=lambda:self.app.handler.changeServer(num), bg=BUTTON_COLOUR)
		button.grid()
		return button
		
	def clear(self, boxes):
		if "Input" in boxes:
			self.chatboxInput.delete('1.0', END)
		if "Output" in boxes:
			self.chatboxText.destroy()
			self.chatboxText = ScrollFrame(self.topMiddle, width=690, height=440, bg=WIDGET_COLOUR)
			self.chatboxText.grid(row=1, column=0, columnspan=2)
		if "Clients" in boxes:
			self.usersScrollFrame.destroy()
			self.usersScrollFrame = ScrollFrame(self.topRight, width=128, height=480, bg=WIDGET_COLOUR)
			self.usersScrollFrame.grid(row=2, column=0, padx=0)
			
	def createClientFrame(self, client, count):
		clientFrame = Label(self.usersScrollFrame.innerFrame, width=14, height=1, text=client.name, bg=WIDGET_COLOUR)
		clientFrame.grid(column=0)
		self.serverUsersLabel.configure(text="%s User(s) Online" % count)
		return clientFrame
		
	def removeClientFrame(self, clientFrame, count):
		clientFrame.destroy()
		self.serverUsersLabel.configure(text="%s User(s) Online" % count)
		
class Window(Toplevel):
	def __init__(self, interface, windowtype, data="", *args, **kwargs):
		Toplevel.__init__(self, interface.root)
		self.interface    = interface
		self.windowtype   = windowtype
		self.top          = Frame(self)
		self.bottom       = Frame(self)
		self.acceptButton = Button(self.bottom, width=10, height=1, text="OK", relief=GROOVE, command=lambda:self.runCommand())
		self.cancelButton = Button(self.bottom, width=10, height=1, text="Cancel", relief=GROOVE, command=self.close)

		self.top.grid(row=0, column=0)
		self.bottom.grid(row=1, column=0)
		self.acceptButton.grid(row=0, column=1, padx=10, pady=10)
		self.cancelButton.grid(row=0, column=0, padx=10, pady=10)
		
		self.title(windowtype)
		self.protocol("WM_DELETE_WINDOW", self.close)

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

	def runCommand(self):
		if self.windowtype == "Log In":
			pass

		elif self.windowtype == "Sign Up":
			pass
		
		elif self.windowtype == "Add Server":
			self.interface.app.handler.addServer(self.ipEntry.get(), self.portEntry.get())

		self.close()

	def close(self):
		self.interface.isWindowOpen = False
		self.destroy()

class ScrollFrame(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, relief=GROOVE, bd=1, *args, **kwargs)
		self.w          = kwargs['width']
		self.h          = kwargs['height']
		self.canvas     = Canvas(self, width=self.w, height=self.h, bg=self.cget('bg'), highlightbackground=self.cget('bg'))
		self.innerFrame = Frame(self.canvas, width=self.w, bg=self.cget('bg'), highlightbackground=self.cget('bg'))
		self.scrollbar  = Scrollbar(self, orient="vertical", command=self.canvas.yview, relief=GROOVE, bg="red", highlightbackground=self.cget('bg'))
		
		self.canvas.grid(row=0, column=0)
		self.innerFrame.grid(row=0, column=0)
		self.scrollbar.grid(row=0, column=1, sticky=N+S)

		self.canvas.configure(yscrollcommand=self.scrollbar.set)
		self.canvas.create_window((0,0), window=self.innerFrame, anchor="nw")
		
class ServerButton(Frame):
	def __init__(self, parent, num, name, *args, **kwargs):
		Frame.__init__(self, parent, bg=parent.cget('bg'))
		self.name         = name
		self.num          = num
		self.serverStatus = Button(self, width=1, height=1, bg="red", relief=FLAT, state=DISABLED)
		self.button     = Button(self, text=self.name, width=14, height=1, relief=GROOVE, state=DISABLED, *args, **kwargs)

		self.serverStatus.grid(row=0, column=0, padx=1, pady=2)
		self.button.grid(row=0, column=1)
		
class MessageBox(Frame):
	def __init__(self, parent, data, sender, *args, **kwargs):
		Frame.__init__(self, parent, bg=parent.cget('bg'))
		self.sender = Label(self, text=sender, height=1, font=("Helvetica", "9", "bold"), bg=self.cget('bg'))
		self.text = Label(self, width=98, height=round((len(data)/98)+0.5), font=("Helvetica", 9), text=data, relief=FLAT, wraplength=690, anchor=NW, justify=LEFT, bg=self.cget('bg'))
		self.separator = Frame(self, height=2, bd=1, relief=SUNKEN, highlightbackground=self.cget('bg'), bg=self.cget('bg'))

		self.sender.grid(row=0, column=0, sticky=N+W)
		self.text.grid(row=1, column=0, sticky=N+W)
		self.separator.grid(row=2, column=0, sticky=E+W, pady=5, padx=2)
