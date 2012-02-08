####
# 
# Usage:
# python vector-to-matrix.py /home/fimz/Dev/datasets/500-results/rev/imbalanced-100/1328050699-newcombined-out.txt
#
import csv,os,sys,numpy,dynamic

def sum_labels(labels, distance_matrix):
	val = {}
	res = {}
	ressum = 0
	global categories
	for label in labels:
	   part1Class, part1Details = label.split("-")
	   category1 = dynamic.categorisePayload(part1Class, categories)           # Classify the header -> return 14 for 14.1, 14.1.1, 14.1.2
	   for i in range(0,len(labels)):
		part2Class, part2Details = labels[i].split("-")
		category2 = dynamic.categorisePayload(part2Class, categories)
		if category1 == category2 :  ## Match main category or sub-cat
			if label in val:
			       val[label].append(distance_matrix[labels.index(label)][i]) ## Append values from same category
			if label not in val:
			       val[label] = [] ## setup dictionary key for val 
			       res[label] = [] ## setup dicitonary key for res
			       val[label].append(distance_matrix[labels.index(label)][i]) ## Append corresponding values from same category
	   ressum = 0
	   for item in val[label]:      ## for every item in the dictionary key
		ressum = ressum + item  ## Add each item with its predecessor
	   res[label].append(ressum)    ## Append the sum to the result corresponding the label
	return res,val  ## return result and val dict


def matrix_from_pairs(pairs):
    """Takes a list of pairs and their distances and creates the distance matrix.

    The list elements should have the format:

        (name1, name2, value)

    It will return a matrix with all the values, plus the list of labels.
    """

    labels = set()
    labels.update([x[0] for x in pairs]+[x[1] for x in pairs])
    labels = list(labels)
    labels.sort()

    dimension = len(labels)
    distance_matrix = numpy.zeros( (dimension, dimension), 'f')

    for pair in pairs:
        i = labels.index(pair[0])
        j = labels.index(pair[1])
        distance_matrix[i][j] = float(pair[2])

    return distance_matrix, labels
#===================
# MAIN starts here
#===================
res = {} ## result of the sum
val = {} ## values per sample
sums = {} ## sums per category
ref = {} ## reference of sum and sample
minres = {} ## result for minimum
ressum = 0;
fname = sys.argv[1]
pairs = []
categories, topLevelCategories = dynamic.loadCategories("categories-500.txt") ## Load categories from cat file
resfile = csv.reader(open(fname, 'r'), delimiter=" ")
for row in resfile:
	pairs.append(row)

distance_matrix, labels = matrix_from_pairs(pairs)
hlabels = labels[:]
hlabels.insert(0,0)
writer = csv.writer(open("matrix.csv",'w'),delimiter = ',')
writer.writerow(hlabels)
temp = []
counter = 0
for row in distance_matrix:
   if counter <= max:
        temp = list(row)
        temp.insert(0,labels[counter])
        writer.writerow(temp)
        counter = counter + 1

res,val = sum_labels(labels,distance_matrix) ## Return the sum of all the values for each label and the dictionary of all values
print res
temp = []
score = []
writer.writerow(["Labels and score of matching labels per category"])
for label in labels:
	s = []
	score = []
	for item in res[label]:
		ressum = ressum + item
	print label
	print val[label]
	score = val[label][:]
#	score.append(s)
	score.insert(0,label)
#	,s.format(locals()).strip('"')]
	writer.writerow(score)

#writer.writerow([label,','.join(map(str,val[label]))])
#	sumofcat.append(label+","+resstr)
	
writer.writerow(["Labels,Sum of matches"])
for label in labels:
	writer.writerow([label,','.join(map(str,res[label]))])

for cat in topLevelCategories:
   sums[cat] = []
   minres[cat] = []
   ref[cat] = []
   for label in labels:
	part1Class, part1Details = label.split("-")
	category1 = dynamic.categorisePayload(part1Class, categories)           # Classify the header -> return 14 for 14.1, 14.1.1, 14.1.2
	if cat == category1:  ## need to verify category from label via dynamic functions
		sums[cat].append(res[label])
		ref[cat].append([label,res[label]])
#   print cat
#   print sums[cat]
#   print min(sums[cat])		
   try:
	   minres[cat].append(min(sums[cat]))
	   writer.writerow([cat,"(Labels,Scores)",','.join(map(str,ref[cat])).strip("[]")])
	   writer.writerow([cat,"Minimum:",','.join(map(str,minres[cat])).strip("[]")])
	   for i in range(len(ref[cat])):
		   if ref[cat][i][1] == min(sums[cat]):
			   print ref[cat][i]
			   writer.writerow([cat,"(Label,Min)",ref[cat][i]])
			   writer.writerow([cat,"(Label,MaxT)",max(val[ref[cat][i][0]]) ])

   except ValueError:
	   print "ValueError occured for cat:",cat


