#mStart = 0, mEnd = -1,  Width = 8, mCheck = -1, foldOp = add, finalOp = xor, magicVal = 0x55. 
# calculate the checksum

import operator
import functools
width = 8
def calc(msg, fold_op, final_op, magic_val):
	res = functools.reduce(fold_op, msg, 0)

	if final_op is not None:
		if magic_val is None:
				res = final_op(res)            # unary operation
		else:
				res = final_op(res, magic_val) # binary operation

	# make sure it fits in width bits
	return res & ((1 << width) - 1)


data = """806FA30102B00818
806FA30300800040
806FA30200800041
806FA30400800043
806FA30101810848
806FA30102800848
806FA30100810849
806FA3010480084A
806FA3010080084E
806FA30102A00868
806FA30101A2086B
806FA30102880870
806FA30106800874
806FA30100880876
806FA30102900878
806FA30112800878
1003A30001003806739C9B9400121202
1003A3000100380A74A08E9400121206
1003A30001004006729E99940012120B
1003A30001003007729B9A8E00121212
1003A30001003804747778CC01121212
1003A30001003007719B999000121212
1003A300010030076F9F929400121213
1003A300010030076EA18C9400121214
1003A300010030076EA08E9400121217
1003A30001003007729B9A900012121C
1003A3000100300672A191940012121C
1003A30001003007729B99900012121D
1003A30001003007709C98940012121F
1003A30001003805747677000012122C
1003A3000100B4036C3E3A0000120031""".strip()


# make a list out of the messages
def hexToList(data,pad):
	msgs = []
	if width == 8:
		for m in data.split("\n"):
			if pad and len(m) % 2 != 0:
				m = m + "0"
			msgs.append([x for x in bytes.fromhex(m)])
	else: # it's 16
		for m in data.split("\n"):
			if pad and len(m) % 4 != 0:
				m = m + (4 - (len(m) % 4)) * "0"
			msgs.append([int(m[i:i+4], 16) for i in range(0, len(m)-3, 4)])
	return msgs




# Given a set of bytes, calculate the checksum
def calculate_checksum(payload):
	#res = functools.reduce(operator.add, payload, 0)
	res = 0
	checksum = 0
	for byte in payload:
		checksum=checksum+byte

	if operator.xor is not None:
		if 0x55 is None:
				res = operator.xor(res,0)            # unary operation
		else:
				res = operator.xor(res, 0x55) # binary operation

	# make sure it fits in width bits

	checksum = checksum ^ 0x55
	return checksum & ((1 << width) - 1)
	#return res & ((1 << width) - 1)
	
def calculate_checksum(payload):
	#res = functools.reduce(operator.add, payload, 0)
	magicValue = 0x55
	checksum = 0
	for byte in payload:
		checksum= (checksum+byte)
	checksum = (checksum ^ magicValue)
	return checksum & ((1 << width) - 1)
	#return res & ((1 << width) - 1)

def mk_calculate_checksum(mask,foldOp,finalOp,magicValue):
	print(mask)
	f= f"""    checksum = 0
	for byte in payload:
		checksum = checksum {foldOp} byte
	"""
	if finalOp:
		if magicValue:
			f = f"    magicValue = {str(magicValue)}\n" + f + f"    checksum = checksum {finalOp} magicValue\n"
		else:
			f = f + f"    checksum = {finalOp} checksum\n"
	f = f + f"    return checksum & {str(mask)}"
	return "def calculate_checksum(payload):\n" +f


def mk(mask,foldOp,finalOp,magicValue,mStart,mEnd,cIdx,csumW):
	
	lines = [f"def calculate_checksum(payload):"]
	lines+= [f"	checksum = 0"]
	if magicValue:
		lines+= [f"	magicValue = {magicValue}"]
	lines+= [f"	for byte in payload:"]
	lines+= [f"		checksum = checksum {foldOp} byte"]
	if finalOp:
		if magicValue:
			lines+= [f"	checksum = checksum {finalOp} magicValue"]
		else:
			lines+=	[f"	checksum =  {finalOp}checksum"]
	lines+= [f"	return checksum & {mask}"]
	lines+= [""]
	lines+= [f"def validate_message(msg):"]
	lines+= [f"	msgStart = {mStart}"]
	lines+= [f"	msgEnd = {mEnd}"]
	lines+= [f"	payload = msg[msgStart:msgEnd]"]
	lines+= [f"	checksumStart = {cIdx}"]
	lines+= [f" checksum = msg[checksumStart]"]
	# if cIdx+csumW != 0:
	# 	lines+= [f"	checksumEnd = {cIdx+csumW}"]	
	# 	lines+= [f"	checksum_bytes = bytes(msg[checksumStart:checksumEnd])"]
	# else:
	# 	lines+= [f"	checksumBytes = bytes(msg[checksumStart:])"]
	# lines+= [f"	checksum = int.from_bytes(checksumBytes,byteorder='big')"]
	lines+= [f"	return calculate_checksum(payload) == checksum"]
	lines+= [""]
	lines+= [f"assert(validate_message([1,2,3]+[calculate_checksum([1,2,3])])==True)"]
	return "\n".join(lines)

	
def xcalculate_checksum(payload):
	magicValue = 0x55
	checksum = 0
	for byte in payload:
		checksum = checksum + byte
	checksum = checksum ^ magicValue
	return checksum & 255

def xcalculate_checksum(payload):
	magicValue = 85
	checksum = 0
	for byte in payload:
		checksum = checksum + byte
	checksum = checksum ^ magicValue
	return checksum & 255

# Given a msg, validate that no errors have been introduced.
def validate_checksum(msg):

	mStart = 0
	mEnd = -1 
	payload = msg[mStart:mEnd]
	checksum = msg[mEnd:]
	return calculate_checksum(payload) == checksum 


for msg in hexToList(data,False):
	#mStart = 0, mEnd = -1,  Width = 8, mCheck = -1, foldOp = add, finalOp = xor, magicVal = 0x55. 
	v= calc(msg[:-1],operator.add,operator.xor,0x55)
	v2 = calculate_checksum(msg[:-1])
	v3 = xcalculate_checksum(msg[:-1])
	print(msg,v,v2,v3)


def opname2function(name):
	if name == "add":
		return "+"
	elif name == "twosComp":
		return "-"
	elif name =="xor":
		return "^"
	elif name == "":
		pass


ftxt = mk_calculate_checksum(str(0xFF),"+","^",str(0x55))
print(ftxt)
ftxt = mk(0xffff,"-","+",0xfffd,0,0,5,2)
print(ftxt)


print("*"*80)
# def calculate_checksum(payload):
# 	checksum = 0
# 	magicValue = 85
# 	for byte in payload:
# 		checksum = checksum + byte
# 	checksum = checksum ^ magicValue
# 	return checksum & 255

# def validate_message(msg):
# 	msgStart = 0
# 	msgEnd = -1
# 	payload = msg[msgStart:msgEnd]
# 	checksumStart = -1
# 	checksumBytes = bytes(msg[checksumStart:])
# 	checksum = int.from_bytes(checksumBytes,byteorder='big')
# 	return calculate_checksum(payload) == checksum

# assert(validate_message([1,2,3]+[calculate_checksum([1,2,3])])==True)



# assert(validate_message([1,2,3]+[calculate_checksum([1,2,3])])==True)




print("""


def pad(xs,w):
	n = len(xs)
	target_n = (-(-n//w)) * w
	delta = target_n - n
	xs_padded = xs+[0]*delta
	return xs_padded

def chunk(xs,w):
	xs_chunked = [xs[i:i+w] for i in range(0,len(xs),w)]
	return xs_chunked

def to_int(x):
	return int.from_bytes(bytes(x),'big')


def preprocess(xs,w):
	xs_padded = pad(xs,w)
	xs_chunked = chunk(xs_padded,w)
	xs_ints = [to_int(x) for x in xs_chunked]
	return xs_int

""")
def test(msgStart,msgEnd,checksumPos,width,foldOp,finalOp,magicValue,mask):
	def pad(xs,w):
		n = len(xs)
		target_n = (-(-n//w)) * w
		delta = target_n - n
		xs_padded = xs+[0]*delta
		return xs_padded

	def chunk(xs,w):
		xs_chunked = [xs[i:i+w] for i in range(0,len(xs),w)]
		return xs_chunked

	def to_int(x):
		return int.from_bytes(bytes(x),'big')


	def preprocess(xs,w):
		xs_padded = pad(xs,w)
		xs_chunked = chunk(xs_padded,w)
		xs_ints = [to_int(x) for x in xs_chunked]
		return xs_ints


	def calculate_checksum(payload):

		magicValue = 65533
		mask = 0xFFFF

		checksum = 0
		for element in payload:
			checksum = checksum - element
		checksum = checksum + magicValue
		return checksum & mask

	def validate_message(rawmsg):

		msgStart = {0}
		msgEnd = 0
		checksumPos =5 
		width = 2

		msg = preprocess(rawmsg,width)
		payload = msg[msgStart:]
		checksum = msg[checksumPos]
		payload[checksumStart] = 0

		return calculate_checksum(payload) == checksum

def stest(msgStart,msgEnd,checksumPos,width,foldOp,finalOp,magicValue,mask):

	if finalOp != None: 
		if magicValue != None:
			magicValue_str = f"""	magicValue = {magicValue}"""
			finalOp_str = f"""	checksum =  checksum {finalOp} magicValue"""
		else:
			magicValue_str = ""
			finalOp_str = f"""	checksum =  {finalOp}checksum"""
	else:
		magicValue_str = ""
		finalOp_str = ""
	if msgEnd == 0:
		payload_str = f"	payload = msg[msgStart:]"
	else:
		payload_str = f"	payload = msg[msgStart:{msgEnd}]"

	res = f"""
def pad(xs,w):
	n = len(xs)
	target_n = (-(-n//w)) * w
	delta = target_n - n
	xs_padded = xs+[0]*delta
	return xs_padded

def chunk(xs,w):
	xs_chunked = [xs[i:i+w] for i in range(0,len(xs),w)]
	return xs_chunked

def to_int(x):
	return int.from_bytes(bytes(x),'big')


def preprocess(xs,w):
	xs_padded = pad(xs,w)
	xs_chunked = chunk(xs_padded,w)
	xs_ints = [to_int(x) for x in xs_chunked]
	return xs_ints


def calculate_checksum(payload):
{magicValue_str}
	mask = {mask}

	checksum = 0
	for element in payload:
		checksum = checksum {foldOp} element
{finalOp_str}
	return checksum & mask

def validate_message(rawmsg):

	msgStart = {msgStart}
	msgEnd = {msgEnd}
	checksumPos ={checksumPos} 
	width = {width}

	msg = preprocess(rawmsg,width)
{payload_str}
	checksum = msg[checksumPos]
	payload[checksumStart] = 0

	return calculate_checksum(payload) == checksum"""
	return res

data = """4500002894d00000710654cc0d6b8809c0a80a17
450000282ba700007106bdf50d6b8809c0a80a17
45000028bd27000071062c750d6b8809c0a80a17
4500012c000040004006d998c0a80a170d6b8809
45000052000040004006da72c0a80a170d6b8809
450000de4ef50000391197f28efa406ec0a80a17"""

for msg in hexToList(data,False):
	#mStart = 0, mEnd = -1,  Width = 8, mCheck = -1, foldOp = add, finalOp = xor, magicVal = 0x55. 
	#print(msg,validate_message(msg),preprocess(msg,2))
	pass

gender = "male"
s = "At least, that's what {pronoun} told {subject}.".format(pronoun="he" if gender == "male" else "she",subject="he" if gender == "male" else "she")
print(s)


print(stest(0,0,5,2,"-","+",65533,0xFFFF))
