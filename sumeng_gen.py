import re
import functools
import operator
import sys

from generate_code import code

def H(xs_):

    from collections import Counter
    import math

    # Convert our input list to strings. This lets the counter handle weird data types like lists or bytes
    xs = [str(x) for x in xs_] 

    # Count things up
    qty = Counter(xs)

    # How many things do we have?
    n = len(xs)*1.0

    # This is what we will add the summation to
    tot = 0.0

    # For item in the counter
    for item in qty:
        # Get our quantity
        v = qty[item]*1.0

        # Convert that to a probability
        p =(v/n)

        assert(p<=1) #Can't have probability greater than 1 

        # If our probability is greater than zero:
        if p>=0:
            # Add to the total 
            tot += (p * math.log(p,2))
    return abs(-tot)

# returns True if an algorithm is a duplicate
def duplicate(foldOp, finalOp, magicVal):
    if (finalOp == operator.add or finalOp == operator.xor) and magicVal == 0:
        return True
    if foldOp == operator.add and finalOp == twosComp:
        return True
    if foldOp == operator.sub and finalOp == twosComp:
        return True
    if finalOp == operator.xor and magicVal == ((1 << width) - 1):
        return True

    return False

def readexample(file_name):
    f = open(file_name)
    data = f.read()
    f.close()
    return data

def cleanHex(data):
    data = data.strip()
    data = re.sub(' ','',data)
    data = re.sub('0x','',data)
    data = re.sub(',','',data)
    return data

# Let 0 represent the end of the list
def slice(msg, start, end):
    return msg[start:] if end == 0 else msg[start:end]

# Check that we have more than one value in our candidate checksum bytes. 
def checkpatch(i):
    return len(set([ msg[i] for msg in msgs ])) > 1

# calculate the checksum
def calc(msg, fold_op, final_op, magic_val):
    res = functools.reduce(fold_op, msg, 0)

    if final_op is not None:
        if magic_val is None:
                res = final_op(res)            # unary operation
        else:
                res = final_op(res, magic_val) # binary operation

    # make sure it fits in width bits
    return res & ((1 << width) - 1)

# returns True if the algorithm specified matches the value at candidate_index, False otherwise
def check_algo(msg_start, msg_end, candidate_index, fold_op, final_op, magic_val):
    for msg in msgs:
        checksum = msg[candidate_index]
        msg[candidate_index] = 0        # replace the checksum with 0 for the calculation

        algo_result = calc(slice(msg, msg_start, msg_end), fold_op, final_op, magic_val)

        msg[candidate_index] = checksum # reset it
        if (checksum != algo_result):
            return False
    return True

def report_soln(entropy, msg_start, msg_end, candidate_index, fold_op, final_op, magic_val):
    magic_val = hex(magic_val) if magic_val is not None else None
    print("# entropy:", round(entropy, 3), "start:", msg_start, "end:", msg_end, "check:", candidate_index, "foldOp:", fold_op,"finalOp:", final_op,"magicValue:", magic_val)
    print("# " + "="*80)
    if True:
        print("# Generated Code")
        print("# " + "-"*80)
        print("")
        code_str = code(msg_start, msg_end, candidate_index, fold_op, final_op, magic_val,int(width/8))
        print(code_str)
        print("")
        
        msgs_assert =create_msgs_list(8)
        print("# " + "="*80)
        print("# Unit Tests")
        print("# " + "-"*80)
        print("")
        for m in msgs_assert:
            print(f"print(validate_message({m}),{m})")

# make a list out of the messages
def hexToList(data, pad,width):
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

# Make a nice hex string
def hexs(m):
    return " ".join(map(lambda b: format(b, "02x"), m))

def twosComp(n):
    return -n

def onesComp(n1, n2):
    mod = 1 << width
    result = n1 + n2
    return result if result < mod else (result + 1) % mod              

# given a fold operation and a final operation, find a magic value that 
# works for a particular message
def getMagicVal(m, msg_start, msg_end, candidate_index, foldOp, finalOp):
    checksum = m[candidate_index]
    m[candidate_index] = 0
    msg = slice(m, msg_start, msg_end)

    base = calc(msg, foldOp, None, None)
    m[candidate_index] = checksum # reset the checksum

    mVal = finalOps[finalOp](checksum, base) % (1 << width)
    return mVal

def create_msgs_list(width):
    file_name = sys.argv[2]
    data = readexample(file_name)

    data = cleanHex(data)
    return hexToList(data, True,width) # True = pad the messages

def get_sorted_entropies():
    entropies = []
    for i in checksum_indices:
        checksum_values = []
        for m in msgs:
            checksum_values.append(m[i])
        entropies.append((i, H(checksum_values))) # a list of (index, entropy) tuples

    entropies.sort(key=lambda item: item[1], reverse=True)
    return entropies

def full_search():
    if len(sys.argv) == 3:
        return False
    elif len(sys.argv) == 4 and sys.argv[3] == "-f":
        return True
    else:
        print("usage:", "sumeng3.py", "width", "data_file", "[-f]")
        sys.exit()

# SETUP the constants we will use in the search:
#    full_search
#    width
#    msgs
#    msg_lens
#    min_len 
#    same_len
#    foldOps
#    finalOps
#    checksum_indices
#    num_msgs

full_search = full_search() # false if we want to quit after finding the first solution, true otherwise

width = int(sys.argv[1])
assert(width == 8 or width == 16)

msgs = create_msgs_list(width)

msg_lens = set([len(m) for m in msgs])
min_len = min(msg_lens)
same_len = len(msg_lens) == 1

if not same_len:
    msgs.sort(key=len) # check incorrect algorithms on the shortest examples first

# options for functions that will be passed to the reduce function
foldOps = [operator.xor, operator.add,  onesComp,operator.sub]
#foldOps = [operator.xor]
# final operation options- key is the operation, value is the inverse (unary operations have no inverse)

finalOps = {None: None, twosComp: None, operator.invert: None, operator.add: operator.sub, operator.xor: operator.xor}



foldOps = [operator.xor, operator.add,  onesComp]
#foldOps = [operator.xor]
# final operation options- key is the operation, value is the inverse (unary operations have no inverse)

finalOps = {None: None, twosComp: None, operator.invert: None, operator.xor: operator.xor}




# search both directions if messages are variable lengths
if (same_len):
    checksum_indices = range(0, min_len)
else:
    checksum_indices = range(-min_len, min_len)

# delete checksum indices that have the same value across all messages 
checksum_indices = [i for i in checksum_indices if checkpatch(i)]

entropies = get_sorted_entropies() # a list of (index, entropy) tuples sorted by entropy

num_msgs = len(msgs)

def search_binary_finalOp(start, end, candidate_index, foldOp, finalOp, entropy):
    mVals = set()
    for i, m in enumerate(msgs):
        # determine a magic value for a message and then see if it holds                     
        mVal = getMagicVal(m, start, end, candidate_index, 
                            foldOp, finalOp) # finalOps[finalOp] = inverse function 
        mVals.add(mVal)

        if len(mVals) > 1: # found a contraction
            mVals.clear()
            return 0
        if i == num_msgs - 1: # found a solution

            report_soln(entropy, start, end, candidate_index, foldOp, finalOp, mVal)
            mVals.clear()
            if full_search == False:
                sys.exit()
            return 1

def search_unary_finalOp(start, end, candidate_index, foldOp, finalOp, entropy):
    if check_algo(start, end, candidate_index, foldOp, finalOp, None):
        report_soln(entropy, start, end, candidate_index, foldOp, finalOp, None) 
        if full_search == False:
            sys.exit()
        return 1
    return 0

def search():
    counter = 0
    for pairs in entropies:
        candidate_index = pairs[0]
        entropy = pairs[1]

        for msg_start in range(0, min_len):
            for msg_end in reversed(range(msg_start-min_len+1, 1)):

                # skip if the entire message is just the candidate checksum
                if (msg_start-min_len+1 == msg_end and msg_start == candidate_index % min_len):
                    continue

                # check all combinations of fold operations, final operations, and magic values
                for foldOp in foldOps:
                    for finalOp in finalOps.keys():
                        #print("Searching",foldOp,finalOp)
                        if finalOps[finalOp] is not None: # it's a binary final operation
                            counter = counter + search_binary_finalOp(msg_start, msg_end, candidate_index, foldOp, finalOp, entropy)
                        else: # unary operation
                            counter = counter + search_unary_finalOp(msg_start, msg_end, candidate_index, foldOp, finalOp, entropy)

    #print(counter)


# print(onesComp(1,2))
# print (~(1+2))

search()

