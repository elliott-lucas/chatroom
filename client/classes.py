class Message():
	def __init__(self, mode, sender, recipient, data, encrypt):
		self.mode      = mode
		self.sender    = sender
		self.recipient = recipient
		self.data      = data
		self.username  = "Username"
		self.encrypt   = encrypt
	def Construct(self):
		return "".join([self.mode, self.sender, self.recipient, self.data])
		
class Client():
	def __init__(self, refID, name="Username"):
		self.name  = name
		self.refID = refID
	def __repr__(self):
		return ("[%s/%s]" % (self.refID, self.name))
	def __eq__(self, other):
		return self.refID == other.refID
