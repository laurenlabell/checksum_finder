def code(msgStart,msgEnd,checksumPos,foldOp,finalOp,magicValue,width):

	import operator

	# # options for functions that will be passed to the reduce function
	# foldOps = [operator.xor, operator.add, operator.sub, onesComp]
	# #foldOps = [operator.xor]
	# # final operation options- key is the operation, value is the inverse (unary operations have no inverse)

	# finalOps = {None: None, twosComp: None, operator.invert: None, operator.add: operator.sub, operator.xor: operator.xor}


	def foldOp2str(foldOp):
		if foldOp == operator.add:
			return "operator.add"
		elif foldOp == operator.sub:
			return "operator.sub"
		elif foldOp == operator.xor:
			return "operator.xor"
		else:
			return "onesComp"

	def finalOp2str(finalOp):
		if finalOp == operator.invert:
			return "operator.invert"
		elif finalOp == operator.add:
			return "operator.add"
		elif finalOp == operator.sub:
			return "operator.sub"
		elif finalOp == operator.xor:
			return "operator.xor"
		else:
			return str(finalOp)+"-"

	if foldOp != None:
		foldOp = foldOp2str(foldOp)


	if finalOp != None:
		finalOp = finalOp2str(finalOp)

	mask_str = "0x" + "FF" * width

	if finalOp != None: 
		if magicValue != None:
			magicValue_str = f"""	magicValue = {magicValue}"""
			finalOp_str = f"""	checksum =  {finalOp}(checksum,magicValue)"""
		else:
			magicValue_str = ""
			finalOp_str = f"""	checksum =  {finalOp}(checksum)"""
	else:
		magicValue_str = ""
		finalOp_str = ""
	if msgEnd == 0:
		payload_str = f"	payload = msg[msgStart:]"
	else:
		payload_str = f"	payload = msg[msgStart:{msgEnd}]"

	res = f"""

import operator

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
	mask = {mask_str}

	checksum = 0
	for element in payload:
		checksum = {foldOp}(checksum,element)
{finalOp_str}
	return checksum & mask

def validate_message(rawmsg):
	msgStart = {msgStart}
	msgEnd = {msgEnd}
	checksumPos = {checksumPos} 
	width = {width}

	msg = preprocess(rawmsg,width)
{payload_str}
	checksum = msg[checksumPos]
	payload[checksumPos] = 0

	return calculate_checksum(payload) == checksum"""
	return res