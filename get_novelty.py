#######################################################
# 
# Usage:
# python get_mdl.py /home/fimz/Dev/datasets/500-results/rev/imbalanced-100/1328050699-newcombined-out.txt
#
#20120418
#	$ python get_novelty.py
#	All the paths to the folders are hardcoded
#
#######################################################
import csv,os,sys,numpy,dynamic,math,pickle
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
		''' #Changes done for Novelty algo. All samples should be treated as unknown
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
		'''

		if label in possfpval:
		       possfpval[label].append(distance_matrix[labels.index(label)][i]) ## Append values from diff category
		       possfp_labels[label].append(labels[i]) ## Append corresponding label for the values from diff category

		if label not in possfpval:
		       possfpval[label] = [] ## setup dictionary key for fpval 
		       possfp_labels[label] = []
 		       res[label] = [] ## setup dicitonary key for res
		       possfpval[label].append(distance_matrix[labels.index(label)][i]) ## Append corresponding values from same category
		       possfp_labels[label].append(labels[i]) ## Append corresponding label for the values from same category
		
	   ressum = 0
#	   for item in val[label]:      ## for every item in the dictionary key
#		ressum = ressum + item  ## Add each item with its predecessor
#	   res[label].append(ressum)    ## Append the sum to the result corresponding the label
	   for item in possfpval[label]:
		   ressum = ressum + item
	   res[label].append(ressum) 	
#	return possfpval,possfp_labels,res,val,match_labels  ## return result and val dict
	return possfpval,possfp_labels,res  ## return result and val dict


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

########################################
# Check possible fp with this threshold
#########################################
#def check_fp(possfp_labels,possfpval,fp_labels,fpval,val,cat,exemplar,ex_thresh,writer):
def check_fp(cat,exemplar,ex_thresh,writer):
   print "IN FP"
   print "Exemplar:", exemplar
   global possfp_labels
   global possfpval
   global fp_labels
   global fpval
   global val
   
   has_fp = 0
   fpcount = 0
   minfp = 0
#   print "Len:",len(possfpval[exemplar])
#   print "Range:",range(len(possfpval[exemplar]))
   for z in range(len(possfpval[exemplar])):
#	   print "z:",z
#	   print "possfpval:", possfpval[exemplar][z]
#	   print "Max",max(val[exemplar])
	if possfp_labels[exemplar][z] in mymodel:
	   if possfpval[exemplar][z] < ex_thresh:  ## if value is less than the threshold
#		print "GOT A FP VALUE HERE!"
		if exemplar in fpval:
		   fp_labels[exemplar].append(possfp_labels[exemplar][z])
		   fpval[exemplar].append(possfpval[exemplar][z])
		else:
		   fpval[exemplar] = []
		   fpval[exemplar].append(possfpval[exemplar][z])
		   fp_labels[exemplar] = []
		   fp_labels[exemplar].append(possfp_labels[exemplar][z])
		has_fp = 1  ## sample has fp, need to revise model
		fpcount = fpcount + 1 ## fp counter
#					temp = val[ref[cat][i][0]][:]
#   print "Mid check_fp exemplar",exemplar
   if exemplar in fp_labels and fpcount > 0: 
	print "FP result written out to file"
	writer.writerow([cat,"FP labels:",fp_labels[exemplar] ])
	writer.writerow([cat,"FP values:",fpval[exemplar] ])
	writer.writerow([cat,"FP count:",fpcount ])
	minfp = min(fpval[exemplar])
	writer.writerow([cat,"FP MIN:",minfp ])
	writer.writerow([cat,"Threshold that caused FP:",ex_thresh ])
	writer.writerow([cat,"LABEL that caused FP:",exemplar ])
	return has_fp, fpcount, fp_labels, fpval, minfp ## added min fp val
   else:
	has_fp = 0
	fpcount = 0
	minfp = 0
	writer.writerow([cat,"NO FP FOUND FOR THIS LABEL"])
	return has_fp, fpcount, fp_labels, fpval, minfp ## added min fp val

#	print "has_fp:",has_fp
#	print "fpcount:",fpcount
#	print "fp_labels:",fp_labels
#	print "fpval:",fpval
#	print "minfpval", min(fpval[exemplar])
#   print "NO FP FOUnD"
#   print "has_fp:",has_fp
#   print "fpcount:",fpcount
#   print "fp_labels:",fp_labels
#   print "fpval:",fpval
#   print "minfpval", min(fpval[exemplar])
#   print "test"
##########################################

#===========================================================
# Load Model for each class in a dict loadThresh(filename) and labels in a list
#===========================================================
def loadModel(filename):
        global threshDict;
	mymodel = []
        f = open(filename,'r')
        for line in f:
                if line == "": continue  ## ignore empty lines
                line = line.strip()
                ex_label, ex_thresh = line.split(',')
                part1Class, part1Details = ex_label.split("-")
		if ex_label not in mymodel:
			mymodel.append(ex_label)
			threshDict[ex_label] = []
			threshDict[ex_label].append(ex_thresh)
	f.close()
	return mymodel

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
hits = {} ## hits
possfpval = {} ## possible fp values
possfp_labels = {} # possible fp labels
fpval = {} ## fp value
fp_labels = {} ## fp label
model = {}
match_score = {}
outlier_lab = {} ## for outlier labels
outlier_val = {} ## for outlier values
split_thresh = 0 ## split threshold for the exemplar
manual_split_thresh = 0.25 ## split incase no fp
add =0
count = 0
ressum = 0;
mymodel = []
threshDict = {}
#fname = sys.argv[1]
pairs = []
categories, topLevelCategories = dynamic.loadCategories("categories-500.txt") ## Load categories from cat file
## Load the model file
mymodel = loadModel("mymodel.txt")
## Load the outlier pickle set
myoutlier = pickle.load(open("outlier.pkl",'rb'))
os.system("rm -rf /home/fimz/Dev/scripts/novelty")
## DATA DIR
datadir = sys.argv[1]
## Create a directory and copy samples from both lists to this dir
os.system("mkdir novelty")


for item in mymodel:
	os.system("cp ~/Dev/datasets/balanced-raw/imbalanced-500/"+item+" novelty/") ## copy exemplars to novelty/
	os.system("cp "+ datadir +"/"+item+" novelty/") ## copy exemplars to novelty/

for item in myoutlier:
#	os.system("cp ~/Dev/datasets/testset-2/"+item+" novelty/")	## copy outliers to novelty/
	os.system("cp "+datadir+"/"+item+" novelty/")	## copy outliers to novelty/

## Run shell script on this dir to create a distance matrix, which will be the new fname
#resultdir = "/home/fimz/Dev/datasets/500-results/rev/novelty"  ## result directory path
## result dir
resultdir = sys.argv[2]
#os.system("python rev-combncdspam.py --sigdir /home/fimz/Dev/scripts/novelty --datdir /home/fimz/Dev/scripts/novelty --iter 1 --outdir "+resultdir)
os.system("python get_scores.py --sigdir /home/fimz/Dev/scripts/novelty --datdir /home/fimz/Dev/scripts/novelty --iter 1 --outdir "+resultdir)
os.system("mv /home/fimz/Dev/scripts/output/* "+resultdir)

fname = open("result.file",'r').read()

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
#####################################################
 ## Return the sum of all the values for each label and the dictionary of all values including dict of possible fp valuesa and labels

#possfpval,possfp_labels,res,val,match_labels = sum_labels(labels,distance_matrix)#####################################################
possfpval,possfp_labels,res = sum_labels(labels,distance_matrix)#####################################################

#print res
temp = []
score = []
writer.writerow(["Labels and score of matching labels per category"])

# labels,res,ressum,val,
for label in labels:
   if label not in mymodel: ## sum of non model labels only
	print label   
	s = []
	score = []
	for item in res[label]:
		ressum = ressum + item
#	print label
#	print val[label]
	score = possfpval[label][:] ## novelty
	match_score[label] = [] ## novelty
	match_score[label].append(possfpval[label]) ## store list of values/scores against the given label ## novelyt
#	score.append(s)
	score.insert(0,label)
#	,s.format(locals()).strip('"')]
	writer.writerow(possfp_labels[label])
	writer.writerow(score)
#writer.writerow([label,','.join(map(str,val[label]))])
#	sumofcat.append(label+","+resstr)

writer.writerow(["Labels,Sum of matches"])
for label in labels:
	writer.writerow([label,','.join(map(str,res[label]))])

########################################
##### MAIN ITERATOR FOR CALCULATIONS ###
########################################

check_labels = []

for items in possfp_labels:
	check_labels.append(items)
print "Check_labels:", check_labels

sums["samples"]=[]
ref["samples"]=[]
minres["samples"] = []

for cat in topLevelCategories:
   sums[cat] = []
   minres[cat] = []
   ref[cat] = []
for label in labels:
   if label not in mymodel:	   
###	part1Class, part1Details = label.split("-")
###	category1 = dynamic.categorisePayload(part1Class, categories)           # Classify the header -> return 14 for 14.1, 14.1.1, 14.1.2
###	if cat == category1:  ## need to verify category from label via dynamic functions
	sums["samples"].append(res[label])
	ref["samples"].append([label,res[label]])
#   print cat
#   print sums[cat]
#   print min(sums[cat])	
counter = 0
#while(len(check_labels) > 0):
while(len(check_labels) > 0):
	print "##############  NEW RECORD ##################"
	counter = counter + 1
	sums["samples"]=[]
	ref["samples"]=[]
	minres["samples"] = []
	remainder = []
	for label in check_labels:
		if label not in mymodel:
			remainder.append(label)
	if len(remainder) == 0:
		writer.writerow(["Only exemplar labels left. No more processing required"])
		break
 	for label in check_labels:
	   if label not in mymodel:	   
    		sums["samples"].append(res[label])
		ref["samples"].append([label,res[label]])
	   else:
		 print label
	print "mymodel:",len(mymodel)
	print "sums:",sums["samples"]
        print "Min is:",min(sums["samples"])
	minres["samples"].append(min(sums["samples"]))
	writer.writerow([""])
	writer.writerow(["### NEW RECORD ###"])
#	   writer.writerow([cat,"(Labels,Scores)",','.join(map(str,ref[cat])).strip("[]")])
#	   writer.writerow([cat,"Minimum:",','.join(map(str,minres[cat])).strip("[]")])
	for i in range(len(ref["samples"])):
		   if ref["samples"][i][1] == min(sums["samples"]): ## if minimum value in list is same as current cat
			   print "Ref pair:",ref["samples"][i]  ## label and its min value pair
			   writer.writerow(["(Exemplar-Label,Min)",ref["samples"][i]])
			   writer.writerow(["Max Threshold",max(possfpval[ref["samples"][i][0]]) ])
			   writer.writerow(["Matching Labels:"])
			   writer.writerow(possfp_labels[ref["samples"][i][0]]) ## write matching labels per exemplar
			   writer.writerow(["Matching similarity scores:"])
	   	           writer.writerow(match_score[ref["samples"][i][0]]) ## write score of these labels per exemplar
			   model[counter] = []  ## create model
			   model[counter].append([ref["samples"][i][0],max(possfpval[ref["samples"][i][0]])]) ## model with exemplar and threshold pair
			   ### E X E M P L A R S ###
			   exemplar_lab = ref["samples"][i][0] ## Exemplar label
			   exemplar_val = possfpval[ref["samples"][i][0]][:] ## Exemplar value
			   exemplar_thresh = max(possfpval[ref["samples"][i][0]])
			   print "Initial Exemplar: ",exemplar_lab
			   print "Initial thresh: ",exemplar_thresh
			   writer.writerow(["Initial Exemplar: ",exemplar_lab])
			   writer.writerow(["Initial thresh: ",exemplar_thresh])
			   ########################################
			   # Check possible fp with this threshold
			   #########################################
#			   print "Before check_fp"
			   has_fp,fpcount,fp_labels,fpval,fpmin = check_fp(cat,exemplar_lab,exemplar_thresh,writer)
			   ##########################################
			   ### H A S  F A L S E P O S I T I V E S ###
			   ##########################################
			   print "FP labels:", fp_labels
			   print "FP min:", fpmin
			   print "test:",fp_labels[exemplar_lab][fpval[exemplar_lab].index(fpmin)]
			   if (has_fp):
			     ## Run calculations once to create misshits list and then pass it to the iterator ##
			     iteration = 0
			     print "Has FP"
			     matches[exemplar_lab] = []
			     outlier_lab[exemplar_lab] = []
			     outlier_val[exemplar_lab] = []
			     sane = []
			     temp = [] ## for split point
			     count = 0
			     
			     for myscore in possfpval[exemplar_lab]:
				if myscore < 0.85: ## Sanity threshold changed for NCD and spsum
	# 				   print myscore
					   sane.append(myscore)
					   count = count + 1
				else:
					outlier_lab[exemplar_lab].append(possfpval[exemplar_lab])
					outlier_val[exemplar_lab].append(possfpval[exemplar_lab])
#				print "Values:",myscore
				if myscore < fpmin: ## for split thresh
					temp.append(myscore)
			     
			     y1 = numpy.median(sane)  ## Replace avg with median for all values
			     #split_thresh = math.fabs(fpmin - y1)/2.0## the threshold required to split data into groups
#			     print "Temp val:",temp
			     try:
				split_thresh = max(temp)
				writer.writerow(["split max threshold",split_thresh])

			     except ValueError:
				split_thresh = 0
			     if split_thresh == 0: ## if the split threshold is zero, use fpmin - 0.1 as the new split threshold
				     split_thresh =  0.2
			     if split_thresh > 0.8: ## sanity check
			     	     split_thresh = 0.75
	  		     hits[exemplar_lab] = [] ## reset hits and misshits list
			     miss_hits[exemplar_lab] = [] ##
			     writer.writerow(["Count Hit labels",len(miss_hits[exemplar_lab])])
			     writer.writerow(["Count Missmatch labels",len(hits[exemplar_lab])])
			     writer.writerow(["split threshold",split_thresh])

		     
			     for j in range(len(possfpval[exemplar_lab])):
				y2 = possfpval[exemplar_lab][j]
				writer.writerow(["y2:split","%2d %2d" % (y2,split_thresh)])

#				x1 = x2 = 0
#				p1 = [x1,y1]
#				p2 = [x2,y2]
				if float(y2) <= float(split_thresh):  ## Match if eucl dist is below 1.95
#					print "Matching labels:",possfp_labels[exemplar_lab][j]
#					print i,j
					matches[exemplar_lab].append(possfp_labels[exemplar_lab][j]) ## Append labels of matching criteria of eucl distance of < 0.85
					if exemplar_lab in hits:
						hits[exemplar_lab].append(possfp_labels[exemplar_lab][j]) ## append results to hits dictionary
					else:
						hits[exemplar_lab] = [] ## create new dictionary key
						hits[exemplar_lab].append(possfp_labels[exemplar_lab][j]) ## append results tohits dictionary
				else:
#					print "Missmatch labels:",possfp_labels[exemplar_lab][j]
					matches[exemplar_lab].append("MISS-HITS") ## Did not match
					if exemplar_lab in miss_hits:
						 miss_hits[exemplar_lab].append(possfp_labels[exemplar_lab][j]) ## Did not match
					else:
						miss_hits[exemplar_lab] = []
						miss_hits[exemplar_lab].append(possfp_labels[exemplar_lab][j]) ## Did not match
			     			     			     			   

			     writer.writerow(["split threshold",split_thresh])
			     print "split thresh:",split_thresh
#			     writer.writerow([split_thresh])
#			     writer.writerow(["Matching label after euclid"])
#			     writer.writerow(matches[exemplar_lab])
			     new_thresh = float(split_thresh) ## should be the max of values under fpmin 
			     if exemplar_lab in miss_hits:
                                        writer.writerow(["Missmatch Labels"])
                                        writer.writerow(miss_hits[exemplar_lab])
#					print "missmatch labels:",miss_hits[exemplar_lab]
                                        writer.writerow(["Count Missmatch labels",len(miss_hits[exemplar_lab])])
					print "count missmatch labels:",len(miss_hits[exemplar_lab])
					#writer.writerow([len(miss_hits[exemplar_lab])])
			     ## Changes to Model ##
#			     model.pop(cat)
#			     counter = counter + 1
			     model[counter] = []
   			     writer.writerow(["Model Revised in FP:"])
			     model[counter].append([exemplar_lab,new_thresh])
			     writer.writerow(model[counter])
			     
			     ## Call the evaluate_model function ## 
#			     print "match_score:",match_score
#			     print "match_label:",match_labels
#			     new_misshits,newhits,model = evaluate_model(miss_hits[exemplar_lab],match_score,match_labels,cat,writer,model,has_fp,fpmin,iteration)
			     print "Exemplar: ",exemplar_lab
			     print "Threshold: ",new_thresh
			     new_misshits = miss_hits[exemplar_lab][:]
			     new_hits = hits[exemplar_lab][:]
			     print "New hits:",new_hits
                             writer.writerow(["New Hit Labels"])
                             writer.writerow(new_hits)
			     writer.writerow(possfpval[exemplar_lab])
			     writer.writerow(["New hit Labels count:"])
                             writer.writerow([len(new_hits)])
                             writer.writerow([len(hits[exemplar_lab])])
			     writer.writerow(matches[exemplar_lab])

#			     while(len(new_misshits) > 0): ## recall the evaluate_model funct till there are no more misshits ##
 			     iteration = iteration + 1
			     print "New misshits:",new_misshits
#			     model = evaluate_model(new_misshits,new_hits,match_score,match_labels,cat,writer,model,has_fp,fpmin,iteration,exemplar_lab)
			     for items in new_hits:
				     if items in check_labels and items not in mymodel:
					     check_labels.remove(items)

#			     check_labels.remove(exemplar_lab)
			     print "labels left:",len(check_labels)
			     writer.writerow(["labels remaining:"])
			     writer.writerow([len(check_labels)])
			   else: ## NO FP found
				   print "NO FP FOUND !!!"
				   for key,value in model.iteritems():
						for exemplar in value:
							if exemplar[0] == exemplar_lab: ## replace if same exemplar label with new thresh
								exemplar[0] = exemplar_lab
								exemplar[1] = exemplar_thresh
						if key == cat:
							if [exemplar_lab,exemplar_thresh] not in value:
								print "APPEND MODEL IN HITS"
								model[cat].append([exemplar_lab,exemplar_thresh]) ## append exemplar and thresh to model and write it to result file
				   writer.writerow(["MODEL WHEN NO FP: ",model[cat]])
#	except ValueError:
#	   print "ValueError occured for:",exemplar_lab
writer.writerow([""])
writer.writerow(["Model(Median Exemplar, Max Threshold)"])

f = open("novelty_mymodel.txt",'w')
oldmodel = open("mymodel.txt",'a')
for item in model:
	print item
	print model[item]
	print model[item][0][0]
	print model[item][0][1]	
	f.write(str(model[item][0][0])+","+str(model[item][0][1])+"\n")
	oldmodel.write(str(model[item][0][0])+","+str(model[item][0][1])+"\n") ## update the mymodel with new exemplars learned

	print "model:",item
#	writer.writerow(["Model:"])
	writer.writerow([str(model[item][0][0])+","+str(model[item][0][1])])

print "Model:"
print model
os.system("mv matrix.csv "+resultdir+"; mv *.png "+resultdir) ## MOVE RESULTS TO RESULT FOLDER

