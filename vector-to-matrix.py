####
# 
# Usage:
# python vector-to-matrix.py /home/fimz/Dev/datasets/500-results/rev/imbalanced-100/1328050699-newcombined-out.txt
#
#
import csv,os,sys,numpy,dynamic,math
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.mlab as mlab

def euc_dist(p1,p2):
	return math.sqrt(math.pow((p2[0] - p1[0]), 2) +
	                 math.pow((p2[1] - p1[1]), 2) )
               
def plot_scat(x,y,name):
	# Create a figure with size 6 x 6 inches.
	fig = Figure(figsize=(6,6))
	# Create a canvas and add the figure to it.
	canvas = FigureCanvas(fig)
	# Create a subplot.
	ax = fig.add_subplot(111)
	# Set the title.
	ax.set_title("Exemplar "+name,fontsize=14)

	# Set the X Axis label.
	ax.set_xlabel("Packages or Samples",fontsize=12)

	# Set the Y Axis label.
	ax.set_ylabel("Similarity Score",fontsize=12)
	# Display Grid.
	ax.grid(True,linestyle="-",color="0.75")

	# Generate the Scatter Plot.
	ax.scatter(x,y,s=20,color="tomato");

	# Save the generated Scatter Plot to a PNG file.
	canvas.print_figure(name+".png",dpi=300)

def sum_labels(labels, distance_matrix):
	val = {}
	match_labels = {}
	possfpval = {}
	possfp_labels = {}
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
			       match_labels[label].append(labels[i]) ## Append corresponding label for the values from same category
			if label not in val:
			       val[label] = [] ## setup dictionary key for val 
			       match_labels[label] = []
			       res[label] = [] ## setup dicitonary key for res
			       val[label].append(distance_matrix[labels.index(label)][i]) ## Append corresponding values from same category
			       match_labels[label].append(labels[i]) ## Append corresponding label for the values from same category
		else:  ## the categories dont match list of possible fp
			if label in possfpval:
			       possfpval[label].append(distance_matrix[labels.index(label)][i]) ## Append values from diff category
			       possfp_labels[label].append(labels[i]) ## Append corresponding label for the values from diff category
			if label not in possfpval:
			       possfpval[label] = [] ## setup dictionary key for fpval 
			       possfp_labels[label] = []
#			       res[label] = [] ## setup dicitonary key for res
			       possfpval[label].append(distance_matrix[labels.index(label)][i]) ## Append corresponding values from same category
			       possfp_labels[label].append(labels[i]) ## Append corresponding label for the values from same category
		
	   ressum = 0
	   for item in val[label]:      ## for every item in the dictionary key
		ressum = ressum + item  ## Add each item with its predecessor
	   res[label].append(ressum)    ## Append the sum to the result corresponding the label
	return possfpval,possfp_labels,res,val,match_labels  ## return result and val dict


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
maxt = {} ## for sample to threshold mapping per cat
matches = {} ## All matches under the eucl dist of 1.95
match_labels = {} ## All matching labels for that category
miss_hits = {} ## miss hits
possfpval = {} ## possible fp values
possfp_labels = {} # possible fp labels
fpval = {} ## fp value
fp_labels = {} ## fp label
model = {}
match_score = {}
add =0
count = 0
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

possfpval,possfp_labels,res,val,match_labels = sum_labels(labels,distance_matrix) ## Return the sum of all the values for each label and the dictionary of all values
print res
temp = []
score = []
writer.writerow(["Labels and score of matching labels per category"])
for label in labels:
	s = []
	score = []
	for item in res[label]:
		ressum = ressum + item
#	print label
#	print val[label]
	score = val[label][:]
	match_score[label] = []
	match_score[label].append(val[label])
#	score.append(s)
	score.insert(0,label)
#	,s.format(locals()).strip('"')]
	writer.writerow(match_labels[label])
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
	   writer.writerow([""])
	   writer.writerow(["### NEW RECORD ###"])
	   writer.writerow([cat,"(Labels,Scores)",','.join(map(str,ref[cat])).strip("[]")])
	   writer.writerow([cat,"Minimum:",','.join(map(str,minres[cat])).strip("[]")])
	   for i in range(len(ref[cat])):
		   if ref[cat][i][1] == min(sums[cat]): ## if minimum value in list is same as current cat
#			   print ref[cat][i]  ## label and its min value pair
			   writer.writerow([cat,"(Label,Min)",ref[cat][i]])
			   writer.writerow([cat,"Max Threshold",max(val[ref[cat][i][0]]) ])
		           writer.writerow(match_labels[ref[cat][i][0]]) ## write matching labels per exemplar
	   	           writer.writerow(match_score[ref[cat][i][0]]) ## write score of these labels per exemplar
			   model[cat] = []  ## create model
			   model[cat].append([ref[cat][i][0],max(val[ref[cat][i][0]])]) ## model with exemplar and threshold pair
			   ########################################
			   # Check possible fp with this threshold
			   #########################################
			   has_fp = 0
			   fpcount = 0
			   for z in range(len(possfpval[ref[cat][i][0]])):
#			   for z in range(len(dist)):
				   if possfpval[ref[cat][i][0]][z] < max(val[ref[cat][i][0]]):  ## if value is less than the threshold
   				        if ref[cat][i][0] in fpval:
					   fp_labels[ref[cat][i][0]].append(possfp_labels[ref[cat][i][0]][z])
					   fpval[ref[cat][i][0]].append(possfpval[ref[cat][i][0]][z])
					else:
					   fpval[ref[cat][i][0]] = []
					   fpval[ref[cat][i][0]].append(possfpval[ref[cat][i][0]][z])
					   fp_labels[ref[cat][i][0]] = []
					   fp_labels[ref[cat][i][0]].append(possfp_labels[ref[cat][i][0]][z])
					has_fp = 1  ## sample has fp, need to revise model
					fpcount = fpcount + 1 ## fp counter
#					temp = val[ref[cat][i][0]][:]
			   if ref[cat][i][0] in fp_labels: 
 			        writer.writerow([cat,"FP labels:",fp_labels[ref[cat][i][0]] ])
				writer.writerow([cat,"FP values:",fpval[ref[cat][i][0]] ])
				writer.writerow([cat,"FP count:",fpval[ref[cat][i][0]] ])
			   ##########################################
			   matches[ref[cat][i][0]] = []
			   sane = []
			   count = 0
			   for myscore in val[ref[cat][i][0]]:
				if myscore < 0.75: ## Sanity threshold changed for NCD and spsum
# 				   print myscore
				   sane.append(myscore)
				   count = count + 1
#			   y1 = add/count  ## Average of possible result values
#			   x1 = len(val[ref[cat][i][0]])/2
#			   p1 = [x1,y1]
#			   y1 = numpy.median(val[ref[cat][i][0]])  ## Replace avg with median for all values
			   y1 = numpy.median(sane)  ## Replace avg with median for all values
			   for j in range(len(val[ref[cat][i][0]])):
				y2 = val[ref[cat][i][0]][j]
				x2 = j
				p1 = [j,y1]
				p2 = [x2,y2]
				if ( (euc_dist(p1,p2) < 0.4 and y2 < 0.75) or (y2 < 0.3) ):  ## Match if eucl dist is below 1.95
#					print match_labels[ref[cat][i][0]][j]
#					print i,j
					matches[ref[cat][i][0]].append(match_labels[ref[cat][i][0]][j]) ## Append labels of matching criteria of eucl distance of < 1.96
				else:
					matches[ref[cat][i][0]].append("MISS-HITS") ## Did not match
					if ref[cat][i][0] in miss_hits:
						 miss_hits[ref[cat][i][0]].append(match_labels[ref[cat][i][0]][j]) ## Did not match
					else:
						miss_hits[ref[cat][i][0]] = []
						miss_hits[ref[cat][i][0]].append(match_labels[ref[cat][i][0]][j]) ## Did not match
			   writer.writerow(["Euclidean Distance, Matching Labels, Missmatch Labels"])
			   writer.writerow([ euc_dist( [j,y1],[j,val[ref[cat][i][0]][j]]) for j in range(len(val[ref[cat][i][0]])) ])
			   writer.writerow(matches[ref[cat][i][0]])
			   if ref[cat][i][0] in miss_hits:
				writer.writerow(miss_hits[ref[cat][i][0]])
				if len(miss_hits[ref[cat][i][0]]) == 1: ## create model with additional exemplar and tight threshold
	  			   if has_fp == 1 and fpcount > 0: ## update/revise model with new threshold
	   			       tempval = val[ref[cat][i][0]][:]
				       del tempval[matches[ref[cat][i][0]].index("MISS-HITS")] ## delete miss hit value
				       writer.writerow(["MODEL REVISED"])
				       model[cat] = []
				       model[cat] = [ ref[cat][i][0],max(tempval) ] ## recreate model with adjusted threshold
				   model[cat].append([ ref[cat][i][0],0.1  ])
				else:  ## Handle more than 1 miss matches here
					1	
			   writer.writerow(["MODEL: ",model[cat]])
			   maxt[cat] = []
			   maxt[cat].append(ref[cat][i][0])
			   maxt[cat].append( max(val[ref[cat][i][0]]) )
   except ValueError:
	   print "ValueError occured for cat:",cat

writer.writerow(["Model(Median Exemplar, Max Threshold)"])
for cat in topLevelCategories:
   t = []
   x = []
   y = []
   try:
	t = maxt[cat][:]
	print t
	writer.writerow(t)
	y = val[t[0]][:]
	x = range(0,len(y))
#	x = match_labels[t[0]][:]
	plot_scat(x,y,t[0])
   except KeyError:
	   print "Key Error:",cat
