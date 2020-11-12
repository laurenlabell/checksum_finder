# Checksum Finder

Try it on google colab: https://colab.research.google.com/github/laurenlabell/checksum_finder/blob/master/ChecksumFinder.ipynb


Usage: `python3 sumeng_module.py 8 test1.txt ` 

Running against the Tufts Checksum Corpus: `python3 test_corpus`

````
python3 sumeng_module.py 8 test1.txt 
	0 	entropy: 2.585	perc_used: 1.0	start: 0	end: 0	checksum_index: -1	fold_op: <built-in function add>	final_op: <built-in function xor>	magic: 0x55
	1 	entropy: 2.585	perc_used: 0.92	start: 0	end: -1	checksum_index: -1	fold_op: <built-in function add>	final_op: <built-in function xor>	magic: 0x55
Solution number to gen code for? :0
#  start: 0 end: 0 check: -1 foldOp: <built-in function add> finalOp: <built-in function xor> magicValue: 0x55
# ================================================================================
# Generated Code
# --------------------------------------------------------------------------------



import operator

def twosComp(n):
    return -n

def onesComp(n1, n2):
    mod = 1 << 8
    result = n1 + n2
    return result if result < mod else (result + 1) % mod  

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


def preprocess(hex_str,w):
	xs = [x for x in bytes.fromhex(hex_str)]
	xs_padded = pad(xs,w)
	xs_chunked = chunk(xs_padded,w)
	xs_ints = [to_int(x) for x in xs_chunked]
	return xs_ints


def calculate_checksum(payload):
	magicValue = 0x55
	mask = 0xFF

	checksum = 0
	for element in payload:
		checksum = operator.add(checksum,element)
	checksum =  operator.xor(checksum,magicValue)
	return checksum & mask

def validate_message(rawmsg):
	msgStart = 0
	msgEnd = 0
	checksumPos = -1 
	width = 1

	msg = preprocess(rawmsg,width)
	payload = msg[msgStart:]
	checksum = msg[checksumPos]
	payload[checksumPos] = 0

	return calculate_checksum(payload) == checksum

# ================================================================================
# Unit Tests
# --------------------------------------------------------------------------------

print(validate_message('806FA30102B00818'),'806FA30102B00818')
print(validate_message('806FA30112800878'),'806FA30112800878')
print(validate_message('1003A30001004006729E99940012120B'),'1003A30001004006729E99940012120B')
print(validate_message('1003A30001003007709C98940012121F'),'1003A30001003007709C98940012121F')
print(validate_message('1003A30001003806739C9B9400121202'),'1003A30001003806739C9B9400121202')
print(validate_message('806FA30200800041'),'806FA30200800041')

# --------------------------------------------------------------------------------
# End Generated Code
# --------------------------------------------------------------------------------

````
