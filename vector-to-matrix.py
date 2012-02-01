import csv,os,sys,numpy

def sum_labels(labels, distance_matrix):
	val = {}
	res = {}
	ressum = 0

	for label in labels:
	   for i in range(0,len(labels)):
		if label.split('-')[0] == labels[i].split('-')[0]:
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
res = {}
val = {}
ressum = 0;
fname = sys.argv[1]
pairs = []
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
for label in labels:
	for item in res[label]:
		ressum = ressum + item
	writer.writerow([label,','.join(map(str,val[label]))])
#	sumofcat.append(label+","+resstr)

for label in labels:
	writer.writerow([label,','.join(map(str,res[label]))])



