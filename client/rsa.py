import random
import time

class RSA():
	def __init__(self):
		self.blockSize = 2
		self.primes = [
		3001,3011,3019,3023,3037,3041,3049,3061,3067,3079,3083,3089,3109,3119,3121,
		3137,3163,3167,3169,3181,3187,3191,3203,3209,3217,3221,3229,3251,3253,3257,
		3259,3271,3299,3301,3307,3313,3319,3323,3329,3331,3343,3347,3359,3361,3371,
		3373,3389,3391,3407,3413,3433,3449,3457,3461,3463,3467,3469,3491,3499,3511,
		3517,3527,3529,3533,3539,3541,3547,3557,3559,3571,3581,3583,3593,3607,3613,
		3617,3623,3631,3637,3643,3659,3671,3673,3677,3691,3697,3701,3709,3719,3727,
		3733,3739,3761,3767,3769,3779,3793,3797,3803,3821,3823,3833,3847,3851,3853,
		3863,3877,3881,3889,3907,3911,3917,3919,3923,3929,3931,3943,3947,3967,3989,
		4001,4003,4007,4013,4019,4021,4027,4049,4051,4057,4073,4079,4091,4093,4099,
		4111,4127,4129,4133,4139,4153,4157,4159,4177,4201,4211,4217,4219,4229,4231,
		4241,4243,4253,4259,4261,4271,4273,4283,4289,4297,4327,4337,4339,4349,4357,
		4363,4373,4391,4397,4409,4421,4423,4441,4447,4451,4457,4463,4481,4483,4493,
		4507,4513,4517,4519,4523,4547,4549,4561,4567,4583,4591,4597,4603,4621,4637,
		4639,4643,4649,4651,4657,4663,4673,4679,4691,4703,4721,4723,4729,4733,4751,
		4759,4783,4787,4789,4793,4799,4801,4813,4817,4831,4861,4871,4877,4889,4903,
		4909,4919,4931,4933,4937,4943,4951,4957,4967,4969,4973,4987,4993,4999
		]

	def FindLCM(self, num1, num2):
		return int((num1*num2)/self.FindGCD(num1, num2))

	def FindGCD(self, num1, num2):
		if num1 == 0:
			return num2
		if num2 == 0:
			return num1
		if num1 > num2:
			return self.FindGCD(num2, (num1 % num2))
		if num2 < num1:
			return self.FindGCD(num1, (num2 % num1))

	def FindCoprime(self, num1):
		Coprime_Found = False
		while Coprime_Found == False:
			count = random.randint(2, num1)
			GCD = self.FindGCD(num1, count)
			if GCD == 1 and count > 1 and count < num1:
				Coprime = count
				Coprime_Found = True
		return Coprime

	def FindMMI(self, e, N):
		MMI = None
		for i in range(1, N, 1):
			if (i*e) % N == 1:
				return i

	def Euclidian(self, a, b):
		s_old = 1
		t_old = 0
		r_old = a
		s = 0
		t = 1
		r = b
			  
		while r != 0:
			q = r_old // r
			temp = [r,s,t]
			r = r_old-q*temp[0]
			s = s_old-q*temp[1]
			t = t_old-q*temp[2]

			r_old = temp[0]
			s_old = temp[1]
			t_old = temp[2]

		return abs(s_old)

	def KeyGen(self):
		p = self.primes[random.randint(2, len(self.primes))]
		q = self.primes[random.randint(1, self.primes.index(p))]
		n = p*q
		N = self.FindLCM(p-1, q-1)
		e = self.FindCoprime(N)
		d = self.FindMMI(e, N)
		keyPublic  = "%s/%s" % (n,e)
		keyPrivate = "%s/%s" % (n,d)

		return keyPublic, keyPrivate

	def ModExp(self, num, key):
		exponent = str(bin(int(key[1]))[2:])
		binary	 = list(map(int, list(exponent)))
		modulus	 = int(key[0])
		base	 = num
		ans		 = base
		for i in range(1, len(binary)):
			ans = (ans ** 2) % modulus
			if binary[i] == 1:
				ans = (ans * base) % modulus
		return ans

	def PadMessage(self, message, blockSize):
		messageLength = len(message)
		if messageLength % blockSize != 0:
			paddingNum = blockSize - (messageLength % blockSize)
			message += (" "*paddingNum)
		return message

	def PadChar(self, char):
		charLen = len(char)
		charPadded = ("0"*(4-charLen)+char)
		return charPadded

	def PadBlock(self, block):
		blockLen = len(block)
		blockPadded = ("0"*(8-blockLen)+block)
		return blockPadded

	def BlockSplit(self, message, blockSize):
		messageBlocks = []
		messageChars  = list(message)
		count		  = 0
		for i in range(len(messageChars)//blockSize):
			messageBlocks.append(messageChars[count:count+blockSize])
			count += blockSize
		return messageBlocks
				
	def Encrypt(self, messageRaw, keyPublic):
		keyPublic = list(map(int, keyPublic.split("/")))
		blockSize = 2
		messageEncrypted = ""
		messagePadded = self.PadMessage(messageRaw, blockSize)
		messageBlocks = self.BlockSplit(messagePadded, blockSize)
		for block in messageBlocks:
			blockNum = ""
			for char in block:
				charNum = str(ord(char))
				charPadded = self.PadChar(charNum)
				blockNum += charPadded
			blockNum = int(blockNum)
			blockEncrypted = str(self.ModExp(int(blockNum), keyPublic))
			blockPadded = self.PadBlock(blockEncrypted)
			messageEncrypted += blockPadded
		return messageEncrypted

	def Decrypt(self, messageEncrypted, keyPrivate):
		keyPrivate = list(map(int, keyPrivate.split("/")))
		messageBlocks = []
		messageChars  = []
		count = 0
		for i in range(len(messageEncrypted)//8):
			messageBlocks.append(messageEncrypted[count:count+8])
			count += 8
		for block in messageBlocks:
			blockDecrypted = str(self.ModExp(int(block), keyPrivate))
			blockLen = len(blockDecrypted)
			blockPadded = "0"*(8-blockLen)+blockDecrypted
			charNums = [chr(int(blockPadded[:4])), chr(int(blockPadded[4:]))]
			for i in charNums:
				messageChars.append(i)
		paddingRemoved = False
		while paddingRemoved == False:
			if messageChars[-1] == " ":
				messageChars.pop(-1)
			else:
				paddingRemoved = True
		messageDecrypted = "".join(messageChars)
		return messageDecrypted

if __name__ == "__main__":
	RSAEncryptor = RSA()

	keyStartTime = time.time()
	keyPublic, keyPrivate = "16118411/1588087", "16118411/2940331"#keyPublic, keyPrivate = RSAEncryptor.KeyGen()
	keyEndTime = time.time()

	messageRaw = input("INPUT MESSAGE: ")
	
	print("\nPUBLIC KEY		: %s" % keyPublic)
	print("PRIVATE KEY	  : %s\n" % keyPrivate)

	encStartTime = time.time()
	messageEncrypted = RSAEncryptor.Encrypt(messageRaw, keyPublic)
	encEndTime = time.time()
	print("ENCRYPT OUTPUT : '%s'..." % messageEncrypted[:55])
	print("OUTPUT LENGTH  : %s\n" % len(messageEncrypted))

	decStartTime = time.time()
	messageDecrypted = RSAEncryptor.Decrypt(messageEncrypted, keyPrivate)
	decEndTime = time.time()
	print("DECRYPT OUTPUT : '%s'..." % messageDecrypted[:55])
	print("OUTPUT LENGTH  : %s\n" % len(messageDecrypted))

	print("KEY GEN TIME	  : %s" % str(keyEndTime-keyStartTime))
	print("ENCRYPT TIME	  : %s" % str(encEndTime-encStartTime))
	print("DECRYPT TIME	  : %s" % str(decEndTime-decStartTime))

