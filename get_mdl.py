####
# 
# Usage:
# python get_mdl.py /home/fimz/Dev/datasets/500-results/rev/imbalanced-100/1328050699-newcombined-out.txt
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


#############################################
# Evaluate the Model for more than 1 misshits
##############################################

def evaluate_model(miss_hits,val,ref,cat,writer,model):
	misshit_val = {}
	misshit_lab = {}
	miss_index = {}
	corr_misshit_lab = {}
	corr_misshit_val = {}
	sumbad = {}
	badlab = {}
	sumbad[cat] = []
	badlab[cat] = []
	is_match = []
	newhits = {}
	new_misshits = {}
	writer.writerow(["Evaluate function:"])

#	print "Misshits:",miss_hits

	for item in miss_hits: ## Create list of values and labels of misshit samples
		misshit_val[item] = []
		misshit_lab[item] = []
#		print "Item:",item
#		print "val:",val[item]
#		print "ref:",ref[item]
		misshit_val[item].append(val[item])
		misshit_lab[item].append(ref[item])
#		print "misshit_val:",misshit_val[item]

	for item in miss_hits: ## Create list of the index of misshit samples only
		miss_index[item] = []
		for i in range(len(misshit_lab[item][0])):
#			print "len:",len(misshit_lab[item][0])
#			print "i",i
#			print "item in misshit_lab:", misshit_lab[item][0][i]
			if misshit_lab[item][0][i] in miss_hits: ## index of misshit samples
#				print "Matching index found"
				miss_index[item].append(i)
#	print "missindex:",miss_index
	for item in miss_hits:
		corr_misshit_lab[item] = []
		corr_misshit_val[item] = []
#		print "missindex:",miss_index[item]
		for ind in miss_index[item]: ## Corrected misshit val and lab
#			print "item:",item
#			print "index:",ind
#			print "val:",misshit_val[item][0][0][ind]
#			print "lab:",misshit_lab[item][0][ind]
			corr_misshit_val[item].append(misshit_val[item][0][0][ind])
			corr_misshit_lab[item].append(misshit_lab[item][0][ind])
	
	## Now for MDL calculations ##
	sumbad[cat] = []
	for item in miss_hits: ## create a list of sums of bad samples and their labels
#		print "item",item
#		print "misshitval:",corr_misshit_val[item]
#		print "sum:",sum(corr_misshit_val[item])
		sumbad[cat].append(sum(corr_misshit_val[item]))
		badlab[cat].append(item)
	print "sumbad:",sumbad[cat]
	print "badlab:",badlab[cat]
	mdl_val = min(sumbad[cat]) ## minimum of the sums
	mdl_ind = sumbad[cat].index(min(sumbad[cat])) ## index of the min sum
	mdl_lab = badlab[cat][mdl_ind] ## label of mdl
	print "MDL val:",mdl_val
	print "MDL lab:",mdl_lab
	writer.writerow([cat,"NewLabel,Newmin",mdl_lab,mdl_val])
	writer.writerow([cat,"Max Threshold",max(corr_misshit_val[mdl_lab])])

#	x1 = x2 = y1 = y2 = 0	
	## Now for median and euclid calc ##
	writer.writerow(["New MDL Labels and Scores:"])
	writer.writerow(corr_misshit_lab[mdl_lab])
	writer.writerow(corr_misshit_val[mdl_lab])

	temp = []
	temp = corr_misshit_val[mdl_lab][:]
#	print "mdl values",corr_misshit_val[mdl_lab]
	y1 = numpy.median(temp)
	print "Median: ",y1
	x1 = x2 = 0
	p1 = [x1,y1]
	
	newhits[mdl_lab] = []
	new_misshits[mdl_lab] = []
	eucd = []
	for v in corr_misshit_val[mdl_lab]:
#		print "v:",v
		y2 = v
		p2 = [x2,y2]
#		print "euclid: ",euc_dist(p1,p2)
		eucd.append(euc_dist(p1,p2))
		if ( (euc_dist(p1,p2) < 0.4 and y2 < 0.75) or (y2 < 0.3) ):  ## Match if eucl dist is below 0.75
			newhits[mdl_lab].append(corr_misshit_lab[mdl_lab][corr_misshit_val[mdl_lab].index(v)])
			is_match.append(corr_misshit_lab[mdl_lab][corr_misshit_val[mdl_lab].index(v)])
		else:
			is_match.append("MISS-HIT")
			new_misshits[mdl_lab].append(corr_misshit_lab[mdl_lab][corr_misshit_val[mdl_lab].index(v)])
	
	writer.writerow(["Euclidean distance:"])
	writer.writerow(eucd)
#	writer.writerow([ euc_dist([x1,y1],[x2,j]) for j in corr_misshit_val[mdl_lab] ])
	writer.writerow(is_match) ## write is_match results
	## add revised model ##
#	if has_fp == 1 and fpcount > 0: ## update/revise model with new threshold
#	       tempval = val[ref[cat][i][0]][:]
#	       del tempval[matches[ref[cat][i][0]].index("MISS-HITS")] ## delete miss hit value
	writer.writerow(["MODEL REVISED"])
#	       model[cat] = []
	       ## recreate model with adjusted threshold
	model[cat].append([ mdl_lab,max(corr_misshit_val[mdl_lab]) ])
	writer.writerow(model[cat])

	return new_misshits[mdl_lab], newhits[mdl_lab], model

########################################
# Check possible fp with this threshold
#########################################
def check_fp(possfp_labels,possfpval,fp_labels,fpval,val,cat,exemplar,writer):
   print "IN FP"
   print "Exemplar:", exemplar
   has_fp = 0
   fpcount = 0
   for z in range(len(possfpval[exemplar])):
#	   print z
#	   print "possfpval:", possfpval[exemplar][z]
#	   print "Max",max(val[exemplar])
	   if possfpval[exemplar][z] < max(val[exemplar]):  ## if value is less than the threshold
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
   if exemplar in fp_labels: 
	print "FP result written out to file"
	writer.writerow([cat,"FP labels:",fp_labels[exemplar] ])
	writer.writerow([cat,"FP values:",fpval[exemplar] ])
	writer.writerow([cat,"FP count:",fpcount ])

   return has_fp, fpcount, fp_labels, fpval, min(fpval[exemplar]) ## added min fp val
##########################################



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
#####################################################
 ## Return the sum of all the values for each label and the dictionary of all values including dict of possible fp valuesa and labels

possfpval,possfp_labels,res,val,match_labels = sum_labels(labels,distance_matrix)#####################################################

#print res
temp = []
score = []
writer.writerow(["Labels and score of matching labels per category"])

# labels,res,ressum,val,
for label in labels:
	s = []
	score = []
	for item in res[label]:
		ressum = ressum + item
#	print label
#	print val[label]
	score = val[label][:]
	match_score[label] = []
	match_score[label].append(val[label]) ## store list of values/scores against the given label
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
########################################
##### MAIN ITERATOR FOR CALCULATIONS ###
########################################

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
			   ### E X E M P L A R S ###
			   exemplar_lab = ref[cat][i][0] ## Exemplar label
			   exemplar_val = val[ref[cat][i][0]][:] ## Exemplar value
			   exemplar_thresh = max(val[ref[cat][i][0]])

			   ########################################
			   # Check possible fp with this threshold
			   #########################################
			   has_fp,fpcount,fp_labels,fpval,fpmin = check_fp(possfp_labels,possfpval,fp_labels,fpval,val,cat,exemplar_lab,writer)
			   ##########################################
			   ### H A S  F A L S E P O S I T I V E S ###
			   ##########################################
			   
			   if (has_fp):

			     matches[exemplar_lab] = []
			     outlier_lab[exemplar_lab] = []
			     outlier_val[exemplar_lab] = []
			     sane = []
			     count = 0
			     
			     for myscore in val[exemplar_lab]:
				if myscore < 0.85: ## Sanity threshold changed for NCD and spsum
	# 				   print myscore
					   sane.append(myscore)
					   count = count + 1
				else:
					outlier_lab[exemplar_lab].append(val[exemplar_lab])
					outlier_val[exemplar_lab].append(val[exemplar_lab])

			     y1 = numpy.median(sane)  ## Replace avg with median for all values
			     split_thresh = math.fabs(fpmin - y1)/2.0## the threshold required to split data into groups

			     for j in range(len(val[exemplar_lab])):
				y2 = val[exemplar_lab][j]
				x1 = x2 = 0
				p1 = [x1,y1]
				p2 = [x2,y2]
				if ( (euc_dist(p1,p2) < split_threh and y2 < 0.85) or (y2 < 0.3) ):  ## Match if eucl dist is below 1.95
	#					print match_labels[ref[cat][i][0]][j]
	#					print i,j
					matches[exemplar_lab].append(match_labels[exemplar_lab][j]) ## Append labels of matching criteria of eucl distance of < 1.96
				else:
					matches[ref[exemplar_lab].append("MISS-HITS") ## Did not match
					if exemplar_lab in miss_hits:
						 miss_hits[exemplar_lab].append(match_labels[exemplar_lab][j]) ## Did not match
					else:
						miss_hits[exemplar_lab] = []
						miss_hits[exemplar_lab].append(match_labels[exemplar_lab][j]) ## Did not match
			   
			     new_misshits,newhits,model = evaluate_model(miss_hits[exemplar_lab],match_score,match_labels,cat,writer,model,fpmin)
			     while(len(new_misshits) > 0):

					new_misshits, newhits, model = evaluate_model(new_misshits,match_score,match_labels,cat,writer,model)

			   else:

				   matches[exemplar_lab] = []
				   sane = []
				   count = 0
				   for myscore in val[exemplar_lab]:
					if myscore < 0.85: ## Sanity threshold changed for NCD and spsum
	# 				   print myscore
					   sane.append(myscore)
					   count = count + 1
					else:
						outlier_lab[exemplar_lab].append(val[exemplar_lab])
						outlier_val[exemplar_lab].append(val[exemplar_lab])

	#			   y1 = add/count  ## Average of possible result values
	#			   x1 = len(val[ref[cat][i][0]])/2
	#			   p1 = [x1,y1]
	#			   y1 = numpy.median(val[ref[cat][i][0]])  ## Replace avg with median for all values
				   y1 = numpy.median(sane)  ## Replace avg with median for all values
				   for j in range(len(val[exemplar_lab])):
					y2 = val[exemplar_lab][j]
					x2 = j
					p1 = [j,y1]
					p2 = [x2,y2]
					if ( (euc_dist(p1,p2) < 0.4 and y2 < 0.75) or (y2 < 0.3) ):  ## Match if eucl dist is below 1.95
	#					print match_labels[ref[cat][i][0]][j]
	#					print i,j
						matches[exemplar_lab].append(match_labels[exemplar_lab][j]) ## Append labels of matching criteria of eucl distance of < 1.96
					else:
						matches[ref[exemplar_lab].append("MISS-HITS") ## Did not match
						if exemplar_lab in miss_hits:
							 miss_hits[exemplar_lab].append(match_labels[exemplar_lab][j]) ## Did not match
						else:
							miss_hits[exemplar_lab] = []
							miss_hits[exemplar_lab].append(match_labels[exemplar_lab][j]) ## Did not match
				   writer.writerow(["Euclidean Distance, Matching Labels, Missmatch Labels"])
				   writer.writerow([ euc_dist( [j,y1],[j,val[exemplar_lab][j]]) for j in range(len(val[exemplar_lab])) ])
				   writer.writerow(matches[exemplar_lab])
				   if exemplar_lab in miss_hits:
					writer.writerow(miss_hits[exemplar_lab])
					if len(miss_hits[exemplar_lab]) == 1: ## create model with additional exemplar and tight threshold
					   if has_fp == 1 and fpcount > 0: ## update/revise model with new threshold
					       tempval = val[exemplar_lab][:]
					       del tempval[matches[exemplar_lab].index("MISS-HITS")] ## delete miss hit value
					       writer.writerow(["MODEL REVISED"])
					       model[cat] = []
					       model[cat] = [ exemplar_lab,max(tempval) ] ## recreate model with adjusted threshold
					   model[cat].append([ exemplar_lab,0.1  ])
					else:  ## Handle more than 1 miss matches here
						new_misshits, newhits = evaluate_model(miss_hits[exemplar_lab],match_score,match_labels,cat,writer,model)
	#					while(len(new_misshits) > 0):
	#						new_misshits, newhits = evaluate_model(new_misshits,val,ref,cat,writer)
						print "ok"
						'''
						misscount = len(miss_hits[ref[cat][i][0]]) ##number of miss hits
						tempval = val[ref[cat][i][0]][:] ## values
						templabel = miss_hits[ref[cat][i][0]][:] ## labels
						missindex = []
						leftovers = []
						[ missindex.append(m) for m,x in enumerate(matches[ref[cat][i][0]]) if x == "MISS-HITS"]
						print ref[cat][i][0]
						for ind in sorted(missindex, reverse=True):
							print ind
							print tempval[ind]
							del tempval[ind] ## delete miss hit values
						for lab in templabel:
							leftovers.append(res[lab])
		#				print "New exemplar: ",templabel[leftovers.index(min(leftovers))]
						newlabel = []
						newscore = []
						badindex = []
						exemplist = []
						exemplab = []
	#					for lab in labels:
						newlabel = match_labels[templabel[leftovers.index(min(leftovers))]][:]
						newscore = match_score[templabel[leftovers.index(min(leftovers))]][:]
						for badl in templabel:
							badindex.append(newlabel.index(badl))
							print "badboyz",badl
							print newlabel.index(badl)
						for badi in badindex:
							print "badi:",badi
	#						print match_score[templabel[leftovers.index(min(leftovers))]]
							print match_score[templabel[leftovers.index(min(leftovers))]][0][badi]
							exemplist.append(newscore[0][badi])
							exemplab.append(newlabel[badi])
						print exemplist
						writer.writerow(["New Exemplar",templabel[leftovers.index(min(leftovers))]])	
						writer.writerow(exemplist)
						writer.writerow(exemplab)
						writer.writerow(["Max new:", max(exemplist)])

	'''					
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
