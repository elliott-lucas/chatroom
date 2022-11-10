class Message():
	def __init__(self, mode, sender, recipient, data, encrypt):
		self.mode      = mode
		self.sender    = sender
		self.recipient = recipient
		self.data      = data
		self.username  = "Username"
		self.encrypt   = encrypt
	def construct(self):
		message = "".join([self.mode, self.sender, self.recipient, self.data])
		return message

class Client():
	def __init__(self, refID, connection, address, server, keyPublic=None):
		self.name       = "Username"
		self.refID      = refID
		self.connection = connection
		self.address    = address
		self.ip         = str(address[0])
		self.port       = str(address[1])
		self.server     = server
		self.keyPublic  = keyPublic
		self.isOnline   = False
	def __repr__(self):
		return ("[%s : %s]" % (self.name, str(self.address)))
	def __eq__(self, other):
		return self.refID == other.refID
