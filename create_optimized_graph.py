#
# Use GraphViz to plot a network diagram of
# similarity scores below some threshold. 
# Dataset samples will be displayed as blue nodes 
# and the exemplar/signatures will be displayed as
# green nodes. Class specific Threshold will be provided
# by the get_thresh function. 
# given from 
# 
# Based on:# wjt
# http://digitalhistoryhacks.blogspot.com
## 26 jun 2007
#!/usr/bin/python
import sys
import dynamic ## to access functions from the script

fname = sys.argv[1] ## the file name
output = "output/" ## the output folder
#thres = sys.argv[2]

infile = open(output+fname, 'r') ## open input file in read mode
rows = infile.readlines() ## read lines from file
infile.close()
#print "Threshold is: ",thres
#threshold = float(thres)

categories, topLevelCategories = dynamic.loadCategories("categories-500.txt")
threshDict = dynamic.loadThresh("perclassthresh.txt")        ## load the threshold file and build a dictionary

bios = []
links = []
sig = []

for r in rows:
    row = r.split()
#   print row
#    print "Row[2]=",row[2]
    part1, part2, value = r.split()           # Split the three parts of the line
    part1Class, part1Details = part1.split("-")  # split the first and second headers at the "-" to extract class
    part2Class, part2Details = part2.split("-")
    category1 = dynamic.categorisePayload(part1Class, categories)           # Classify the header -> return 14 for 14.1, 14.1.1, 14.1.2
    category2 = dynamic.categorisePayload(part2Class, categories)
    threshold = dynamic.get_thresh(category2,threshDict)  ## Get threshold value for category
#    print ("class: %s,thresh: %s")%(category2, threshold)
    if float(value) < float(threshold):
	bios.append(part1)
	bios.append(part2)
	sig.append(part2)
	links.append(row)
	# print r,
        
#print list(set(bios))
#print links
outfile = "graph-" + fname
graph_file = open(output+outfile, 'w')
graph_file.write('digraph G {\n')
graph_file.write('\tgraph [overlap=scale];\n')
graph_file.write('\tnode [color=steelblue3];\n')

bios = list(set(bios))
for b in bios:
    if b in sig:
	    graph_file.write('\t' + "\"" +  b + "\"" + ' [color=lawngreen, style=filled];\n')
    else:
	    graph_file.write('\t' + "\"" +  b + "\"" + ' [color=lightblue2, style=filled];\n')

for l in links:
    graph_file.write('\t' + "\"" + l[0] + "\""  + ' -> ' + "\"" +l[1] + "\"" + ' [arrowhead=vee, color=maroon, label = "' + str(l[2]) + '"];\n')

graph_file.write('}')
graph_file.close()

