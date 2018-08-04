import datetime
import time
import json
import hashlib

def rehash(msg):        
	msg = msg.encode('utf-8')
	m = hashlib.sha256()
	m.update(msg)
	return m.hexdigest()

class Block:
	def __init__(self, ledger, sendFrom, sendTo, amount, message):
		if message == "":
			mesage = None
		self.new(ledger, sendFrom, sendTo, amount, message)

	def new(self, ledger, sendFrom, sendTo, amount, message = None): 
		beautify = ""
		for i in range(80):
			beautify = beautify + "-"

		self.transaction = {}
		self.transaction["ID"] = len(ledger)
		self.transaction["From"] = sendFrom
		self.transaction["To"] = sendTo
		self.transaction["Amount"] = float(amount)
		self.transaction["Message"] = message
		self.transaction["Timestamp"] = str(datetime.datetime.now())
		self.transaction["TransactionSignature"] = rehash(str(self.transaction))
		self.transaction["previousLedgerSignature"] = ledger.getHash()
	def get(self):
		return self.transaction

	def verifyTransaction(self):
		tempTransaction = self.transaction.copy()
		del tempTransaction["TransactionSignature"]

		if rehash(str(tempTransaction)) != rehash(str(self.transaction)):
			raise ValueError("Transaction Error: Transaction cannot be verified. Hash does not match")


class Chain:
	def __init__(self):
		self.ledger = []
		self.ledgerHash = None
		self.previousLedgerSignature = None
		self.lastSigned = None

	def add(self, ledger, From, To, Amount, Message):
		t = Block(ledger ,From, To, Amount, Message)
		self.ledger.append(t.get())
		self.sign()
		self.export()

	def sign(self):
		out = json.dumps(self.ledger)
		self.previousLedgerSignature = self.ledgerHash
		self.ledgerHash = rehash(out)
		self.lastSigned = str(datetime.datetime.now()) 

	def __len__(self):
		return len(self.ledger)


	def export(self):
		outfile = open("chain.log", "w")
		outfile.write("Current Hash\t| " + str(self.ledgerHash) + "\n")
		outfile.write("Previous Hash\t| " + str(self.previousLedgerSignature))
		outfile.write("\nSigned \t\t\t| " + str(self.lastSigned))
		outfile.write("\n---------- Begin Ledger ----------\n")
		out = json.dumps(self.ledger)
		outfile.write(out)
		outfile.close()

	def merge(self):
		try:
			infile = open("chain.log", "r")
			print(" Merge: Processing")
			self.ledgerHash = infile.readline()
			if self.ledgerHash == "":
				print("\nEmpty DB Block file detected. Please put the [chain.log] file in the same directory.")
				return
			self.previousLedgerSignature = infile.readline()
			if self.previousLedgerSignature == "":
				print("\nMissing Ledger Signature.")
				return

			self.lastSigned = infile.readline()
			if self.previousLedgerSignature == "":
				print("\nMissing Signature Timestamp.")
				return

			self.ledgerHash = self.ledgerHash.split("|")[1][1:-1]
			self.previousLedgerSignature = self.previousLedgerSignature.split("|")[1][1:-1]
			self.lastSigned = self.lastSigned.split("|")[1][1:-1]
			
			infile.readline()
			outline = infile.read()

			if self.ledgerHash != rehash(outline):
				self.ledgerHash = None
				self.previousLedgerSignature = None
				self.lastSigned = None
				raise KeyError("Hashes do not match")
			print(" Merge Hash:", rehash(outline))
			self.ledger = json.loads(outline)
			print(" Merge: Finished!")
			self.view()
		except IOError:
			infile = open("chain.log", "w")
			print(" Could not find DB File. File created.")
		except KeyError as e:
			print(" Merge Error: " + str(e))
			infile = open("chain.log", "w")
			print(" Deleting dirty chain.")
		finally:
			infile.close()    

	def get(self):
		return self.ledger

	def getHash(self):
		return self.ledgerHash

	def getPreviousHash(self):
		return self.previousLedger

	def view(self):
		print("%25s | %s" % ("Hash", self.ledgerHash))
		print("%25s | %s" % ("Previous Ledger Signature", self.previousLedgerSignature))
		print("%25s | %s" % ("Last Signed", self.lastSigned))
		count = 1
		for i in self.ledger:
			print()
			print("%20s: %-2d" % ("Record", count))
			print("%20s: %-65s" % ("From", i["From"]))
			print("%20s: %-65s" % ("To", i["To"]))
			print("%20s: %-.2f" % ("Amount", i["Amount"]))
			print("%20s: %-30s" % ("Timestamp", i["Timestamp"]))
			print("%20s: %-65s" % ("Signature", i["TransactionSignature"]))
		#	print("%20s: %-65s" % ("Previous Ledger Hash", i["previousLedgerSignature"]))
			count = count + 1

	def __str__(self):
		return str(self.ledger)

	def verifyLedger(self):
		print(self.ledgerHash, rehash(str(self.ledger)))
	
def LogIn():
	users = {}
	users["brandon"] = rehash("pass")
	users["user1"] = rehash("pass1")
	users["user2"] = rehash("user2")

	print()
	print("Log In")

	tryAgain = 1        
	while tryAgain == 1:
		for x in users:
			print(" Added: %-10s [%s]" % (x, users[x]))
		username = input("Enter a username (from above) [Q]uit: ").lower()
		if username[0].lower() == 'q':
			break
		if username in users:
			tryAgain = 0
			print("\nFor this assignment, password has been automatatically entered. #SSO")
			print("Your SHA-256 password hash is: %s. " % users[username])
			user = []
			user.append(username)
			user.append(users[username])
			user.append(users)
			Work(user)
		else:
			print("Nay. Wrong username try again.")

def MainMenu():
	print("%3d: %s" % (0, "Quit"))
	print("%3d: %s" % (1, "Make a Transfer"))
	print("%3d: %s" % (2, "View current ledger"))
	print("%3d: %s" % (3, "Import default Ledger (chain.log)"))
	print("%3d: %s" % (4, "Logout"))

	print()

def Work(uName):
	count = 1
	defaultLedger = Chain()

	print("\nHello " + uName[0])
	keepGoing = -1

	defaultLedger.merge()

	while (keepGoing != 0):
		if (keepGoing == 0):
			break
		print()
		MainMenu()
		keepGoing = int(input("Select an action: "))
		if (keepGoing == 1):
			print(" From: " + uName[0])
			uFrom = uName[0]    
			#amount = 10 * count
			count = count + 1
			#uTo = 'user1'                  
			uTo = input(" Recipient: ")
			if uTo not in uName[2]:
				tryAgain = 1
				while tryAgain == 1:
					uTo = input("  User not found. Try Again. [Q]uit: ")
					if uTo[0].lower() == 'q':
						exit
					else:
						if uTo in uName[2]:
							break

			amount = int(input(" Amount: "))                       
			message = input(" Message (if any):")
			defaultLedger.add(defaultLedger, uFrom, uTo, amount, message)
		elif (keepGoing == 2):
			defaultLedger.view()
		elif (keepGoing == 3):
			defaultLedger.merge()
		elif (keepGoing == 4):
			LogIn()
LogIn()