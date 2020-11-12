

# ------------------------------------------------------------------------------------------------------------------------------------------
# 1 (11047)
example1_msgs = """FC62013010030000140000BD00000000000000000089
FC62013010030000150000BE00000000000000000087
FC62013010030000160000C000000000000000000084
FC620130100300001C0000D00000000000000000006E"""

# 1	-1	21	sub	None	8
example1_sol = { 'msg_start': 1, 'msg_end': -1, 'candidate_index': 21, 'fold_op': 'sub', 'final_op': 'None', 'magic_va': 'None'} #with 8

example1 = (example1_msgs,example1_sol,"11047",8)



examples = []


corpus = []



def parserow(row):
	res = {}
	for i,fname in enumerate(['ID', 'sample', 'msg_start', 'msg_end', 'candidate_index', 'fold_op', 'final_op', 'magic_va', 'width', 'Checksum Algorithm', '# Samples', '# Results', 'Time']):
		res[fname] = row[i].strip()

	
	res["msg_start"] = int(res["msg_start"])
	res["msg_end"] = int(res["msg_end"])
	res["candidate_index"] = int(res["candidate_index"]) 
	res["width"] = int(res["width"])
	if res["magic_va"] == "None":
		res["magic_va"] = None
	if res["final_op"] == "None":
		res["final_op"] = None
	res["sample"] = res["sample"].strip()
	return res

import csv
with open('corpus_summary_full.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in spamreader:
    	if row[1] != "Sample":
	        res = parserow(row)
	        #print(res)
	        if res["sample"] != "Sample":
	        	corpus.append(res)

for c in corpus:
	
	c_sol = { 'msg_start': c['msg_start'], 'msg_end': c['msg_end'], 'candidate_index': c['candidate_index'], 'fold_op': c['fold_op'], 'final_op': c['final_op'], 'magic_va': c['magic_va']} 
	ex = (c["sample"],c_sol,c["ID"],c['width'])
	examples.append(ex)


