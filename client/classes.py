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
    def __init__(self, clientRefID, clientName="Username"):
        self.clientName  = clientName
        self.clientRefID = clientRefID
    def __repr__(self):
        return ("[%s/%s]" % (self.clientRefID, self.clientName))
    def __eq__(self, other):
        return self.clientRefID == other.clientRefID
