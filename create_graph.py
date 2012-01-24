# create_graph.py
#
# Use GraphViz to plot a network diagram of
# similarity scores below some threshold
# 
#
# inspired by wjt
# http://digitalhistoryhacks.blogspot.com
# 
# Fahim 20120117:
# Create sfdp graph showing relationships 
# for any given malware signature sample.
# Requires filename containing scores, 
# the threshold value, and the sample, whose
# relationship is required.

import sys, os

fname = sys.argv[1]
thres = sys.argv[2]
sample = sys.argv[3]

os.system("cp " + fname + " output/")
fstring = fname.split("/")
output = "output/"
mastercat = sample

infile = open(output+fstring[-1], 'r')
rows = infile.readlines()
infile.close()
print "Threshold is: ",thres
threshold = float(thres)
bios = []
links = []
#sig = []

for r in rows:
    row = r.split()
    print row
    print "Row[2]=",row[2]
    category = row[0]
    if ((category in mastercat) or (mastercat in category))  and  float(row[2]) < threshold:
	bios.append(row[0])
	bios.append(row[1])
	#sig.append(row[0])
	links.append(row)
	# print r,
        
#print list(set(bios))
#print links
outfile = "graph-" + sample + ".txt"
graph_file = open(output+outfile, 'w')
graph_file.write('digraph G {\n')
graph_file.write('\tgraph [overlap=scale];\n')
graph_file.write('\tnode [color=steelblue3];\n')

bios = list(set(bios))
for b in bios:
    if sample in b:
	    graph_file.write('\t' + "\"" +  b + "\"" + ' [color=lawngreen, style=filled];\n')
    else:
	    graph_file.write('\t' + "\"" +  b + "\"" + ' [color=lightblue2, style=filled];\n')

for l in links:
    graph_file.write('\t' + "\"" + l[0] + "\""  + ' -> ' + "\"" +l[1] + "\"" + ' [arrowhead=vee, color=maroon, label = "' + str(l[2]) + '"];\n')

graph_file.write('}')
graph_file.close()

os.system("sfdp -Tsvg output/" + outfile  + " -o " + "output/" + outfile +  ".svg")
os.system("mv output/* /home/fimz/Dev/datasets/500-results/single-graph/")
