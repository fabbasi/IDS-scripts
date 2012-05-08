####
# 
# Usage:
# python get_mdl.py /home/fimz/Dev/datasets/500-results/rev/imbalanced-100/1328050699-newcombined-out.txt
# new usage:
# python get_model.py /home/fimz/Dev/datasets/500-results/rev/imbalanced-100/1332124710-newcombined-out.txt
#
# Ive hardcoded alot of pre-requisites in there e.g. all paths to data and sig dir etc
# similarity matrix calculation etc. so now the script can simply be run as:
# $ python get_model.py
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

#########################################
# HANDLING HITS
#########################################

def handle_hits(miss_hits,hits,val,ref,cat,writer,model,has_fp,fpmin,iteration):
	hit_val = {} ## hit value
	hit_lab = {} ## hit labels
	hit_index = {}  ## hit index
	hit_val = {} ## hit value
        hit_lab = {} ## hit labels
        hit_index = {}  ## hit index
	corr_hit_lab = {} ## corrected hit labels, matching labels of only hits
        corr_hit_val = {} ## corrected hit val, matching values of hit labels only.
	sumhit = {}
        hitlab = {}
        sumhit[cat] = []
        hitlab[cat] = []
	is_match = []
        newhits = {}
        new_misshits = {}
	print "Handling HITS"
	writer.writerow(["HANDLING HITS"])

	########### H A N D L I N G  H I T S ############
#	if(has_fp): ## hits,hit_val,hit_lab,hit_index,corr_hit_lab,corr_hit_val
	for item in hits: ## Create list of values and labels of hit samples
		hit_val[item] = []
		hit_lab[item] = []
#		print "Item:",item
#		print "val:",val[item]
#		print "ref:",ref[item]
		hit_val[item].append(val[item])
		hit_lab[item].append(ref[item])
#		print "misshit_val:",misshit_val[item]

	for item in hits: ## Create list of the index of hit samples only
		hit_index[item] = []
		for i in range(len(hit_lab[item][0])):
#			print "len:",len(misshit_lab[item][0])
#			print "i",i
#			print "item in misshit_lab:", misshit_lab[item][0][i]
			if hit_lab[item][0][i] in hits: ## index of misshit samples
#				print "Matching index found"
				hit_index[item].append(i)
#	print "missindex:",miss_index
	for item in hits: ## get values and labels of hits only
		corr_hit_lab[item] = []
		corr_hit_val[item] = []
#		print "missindex:",miss_index[item]
		for ind in hit_index[item]: ## Corrected misshit val and lab
#			print "item:",item
#			print "index:",ind
#			print "val:",misshit_val[item][0][0][ind]
#			print "lab:",misshit_lab[item][0][ind]
			corr_hit_val[item].append(hit_val[item][0][0][ind])
			corr_hit_lab[item].append(hit_lab[item][0][ind])


########## Now for Exemplar calculations ##############

######## HIT EXEMPLAR #########
	sumhit[cat] = []
	for item in hits: ## create a list of sums of hit samples and their labels
#		print "item",item
#		print "misshitval:",corr_misshit_val[item]
#		print "sum:",sum(corr_misshit_val[item])
		sumhit[cat].append(sum(corr_hit_val[item]))
		hitlab[cat].append(item)
#	print "sumhit:",sumhit[cat]
#	print "hitlab:",hitlab[cat]
	hit_exemp_val = min(sumhit[cat]) ## minimum of the sums
	hit_exemp_ind = sumhit[cat].index(min(sumhit[cat])) ## index of the min sum
	hit_exemp_lab = hitlab[cat][hit_exemp_ind] ## label of the min
	print "new exemp hit val:",hit_exemp_val
	print "new exemp hit lab:",hit_exemp_lab
	writer.writerow([cat,"NewExemphit,Newminhit(sum(scores))",hit_exemp_lab,hit_exemp_val])
	writer.writerow([cat,"Max hit Threshold",max(corr_hit_val[hit_exemp_lab])])
	new_max_exemp_thresh = max(corr_hit_val[hit_exemp_lab])
	print "new exemp hit thresh", new_max_exemp_thresh
#	x1 = x2 = y1 = y2 = 0	
	## Now for median and euclid calc ##
	writer.writerow(["New Exemp Labels and Similarity Scores:"])
	writer.writerow(corr_hit_lab[hit_exemp_lab])
	writer.writerow(corr_hit_val[hit_exemp_lab])
	temp = []
	eucd = []
	newhits[hit_exemp_lab] = []
	new_misshits[hit_exemp_lab] = []
	split_thresh = new_max_exemp_thresh
	if split_thresh == 0 or split_thresh < 0.1 :
		split_thresh = 0.2
	for v in corr_hit_val[hit_exemp_lab]:
#		print "v:",v
		y2 = v
		p2 = [x2,y2]
	#	split_thresh
#		print "euclid: ",euc_dist(p1,p2)
		eucd.append(euc_dist(p1,p2))
		if ( (y2 <= split_thresh and y2 < 0.85) or (y2 < 0.4) ):  ## Match if eucl dist is below 0.75
#			print "eucd: ",euc_dist(p1,p2)
			newhits[hit_exemp_lab].append(corr_hit_lab[hit_exemp_lab][corr_hit_val[hit_exemp_lab].index(v)])
			is_match.append(corr_hit_lab[hit_exemp_lab][corr_hit_val[hit_exemp_lab].index(v)])
		else:
			is_match.append("MISS-HIT")
			new_misshits[hit_exemp_lab].append(corr_misshit_lab[hi_exemp_lab][corr_misshit_val[hit_exemp_lab].index(v)])
	writer.writerow(["New split threshold:",split_thresh])	
	writer.writerow(["New Median:",y1])
#	writer.writerow(["Euclidean distance:",eucd])
	writer.writerow(is_match) ## write is_match results
	## add revised model ##
#	writer.writerow(["MODEL REVISED after re-evaluation"])
#	       model[cat] = []
	       ## recreate model with adjusted threshold
	corr_thresh = split_thresh ## corr_thresh = split_thresh = new_max_exemp_thresh = max(corr_hit_val[hit_exemp_lab])
#	model[cat].append([ hit_exemp_lab,corr_thresh ])
	if new_max_exemp_thresh == 0 or new_max_exemp_thresh < 0.1:
		new_max_exemp_thresh = 0.2

	return hit_exemp_lab,new_max_exemp_thresh,newhits[hit_exemp_lab],new_misshits[hit_exemp_lab]

##################################]
# HANDLING MISSHITS
################################
def handle_misshits(miss_hits,hits,val,ref,cat,writer,model,has_fp,fpmin,iteration):
	misshit_val = {} ## misshit value
        misshit_lab = {} ## misshit labels
        miss_index = {}  ## misshit index
        corr_misshit_lab = {}  ## corrected misshit labels
        corr_misshit_val = {}  ## corrected misshit value
        sumbad = {} ## sum of corrected misshits
        badlab = {}
        sumbad[cat] = []
        badlab[cat] = []
        is_match = []
        newhits = {}
        new_misshits = {}
	print "HANDLING MISSHITS"
	writer.writerow(["HANDLING MISSHITS"])
########### H A N D L I N G  M I S S H I T S ########### miss_hits,misshit_val,misshit_lab,miss_index,corr_misshit_val,corr_misshit_lab
	for item in miss_hits: ## Create list of values and labels of misshit samples
		misshit_val[item] = []
		misshit_lab[item] = []
		# print "Item:",item
		# print "val:",val[item]
		# print "ref:",ref[item]
		misshit_val[item].append(val[item])
		misshit_lab[item].append(ref[item])
		# print "misshit_val:",misshit_val[item]

	for item in miss_hits: ## Create list of the index of misshit samples only
		miss_index[item] = []
		for i in range(len(misshit_lab[item][0])):
		# print "len:",len(misshit_lab[item][0])
		# print "i",i
		# print "item in misshit_lab:", misshit_lab[item][0][i]
			if misshit_lab[item][0][i] in miss_hits: ## index of misshit samples
				# print "Matching index found"
				miss_index[item].append(i)
				# print "missindex:",miss_index
	for item in miss_hits:
		corr_misshit_lab[item] = []
		corr_misshit_val[item] = []
		# print "missindex:",miss_index[item]
		for ind in miss_index[item]: ## Corrected misshit val and lab
			# print "item:",item
			# print "index:",ind
			# print "val:",misshit_val[item][0][0][ind]
			# print "lab:",misshit_lab[item][0][ind]
			corr_misshit_val[item].append(misshit_val[item][0][0][ind])
			corr_misshit_lab[item].append(misshit_lab[item][0][ind])


########### H A N D L I N G  H I T S ############
#	if(has_fp): ## hits,hit_val,hit_lab,hit_index,corr_hit_lab,corr_hit_val
	########## Now for Exemplar calculations ##############

	######## HIT EXEMPLAR #########
	

######## MISS HIT EXEMPLAR #########
	## incase of fp check for hits labels and values and evaluate exemplar excluding misshits
	sumbad[cat] = []
	for item in miss_hits: ## create a list of sums of bad samples and their labels
#		print "item",item
#		print "misshitval:",corr_misshit_val[item]
#		print "sum:",sum(corr_misshit_val[item])
		sumbad[cat].append(sum(corr_misshit_val[item]))
		badlab[cat].append(item)
	print "sumbad:",sumbad[cat]
	print "badlab:",badlab[cat]
	exemp_val = min(sumbad[cat]) ## minimum of the sums
	exemp_ind = sumbad[cat].index(min(sumbad[cat])) ## index of the min sum
	exemp_lab = badlab[cat][exemp_ind] ## label of the min
	print "new exemp val:",exemp_val
	print "new exemp lab:",exemp_lab
	writer.writerow([cat,"NewExemp,Newmin(sum(scores))",exemp_lab,exemp_val])
	writer.writerow([cat,"Max Threshold",max(corr_misshit_val[exemp_lab])])
	new_max_exemp_thresh = max(corr_misshit_val[exemp_lab])
	print "new exemp thresh", new_max_exemp_thresh
#	x1 = x2 = y1 = y2 = 0	
	## Now for median and euclid calc ##
	writer.writerow(["New Exemp Labels and Similarity Scores:"])
	writer.writerow(corr_misshit_lab[exemp_lab])
	writer.writerow(corr_misshit_val[exemp_lab])

	temp = []
	temp = corr_misshit_val[exemp_lab][:]
#	print "mdl values",corr_misshit_val[mdl_lab]
	y1 = numpy.median(temp)
	print "Median: ",y1
	x1 = x2 = 0
	p1 = [x1,y1]
        ## should check fp here, but not for now ##	
	newhits[exemp_lab] = []
	new_misshits[exemp_lab] = []
	eucd = []
	split_thresh = new_max_exemp_thresh
	if split_thresh == 0 or split_thresh < 0.1 :
		split_thresh = 0.2

	for v in corr_misshit_val[exemp_lab]:
#		print "v:",v
		y2 = v
		p2 = [x2,y2]
		split_thresh
#		print "euclid: ",euc_dist(p1,p2)
		eucd.append(euc_dist(p1,p2))
		if ( (y2 <= split_thresh and y2 < 0.85) or (y2 < 0.4) ):  ## Match if eucl dist is below 0.75
			newhits[exemp_lab].append(corr_misshit_lab[exemp_lab][corr_misshit_val[exemp_lab].index(v)])
			is_match.append(corr_misshit_lab[exemp_lab][corr_misshit_val[exemp_lab].index(v)])
		else:
			is_match.append("MISS-HIT")
			new_misshits[exemp_lab].append(corr_misshit_lab[exemp_lab][corr_misshit_val[exemp_lab].index(v)])
 	writer.writerow(["New split threshold:",split_thresh])	
	writer.writerow(["New Median:",y1])
#	writer.writerow(["Euclidean distance:",eucd])
	writer.writerow(is_match) ## write is_match results
	## add revised model ##
#	writer.writerow(["MODEL REVISED after re-evaluation"])
#	       model[cat] = []
	       ## recreate model with adjusted threshold
	corr_thresh = split_thresh
	model[cat].append([ exemp_lab,corr_thresh ])

#	writer.writerow(model[cat]) ## write the model to the result file
	if new_max_exemp_thresh == 0 or new_max_exemp_thresh < 0.1:
		new_max_exemp_thresh = 0.2 ## so it can match similar items

	return exemp_lab,new_max_exemp_thresh,newhits[exemp_lab],new_misshits[exemp_lab]


#############################################
# Evaluate the Model for more than 1 misshits
##############################################

def evaluate_model(miss_hits,hits,val,ref,cat,writer,model,has_fp,fpmin,iteration):
	misshit_val = {} ## misshit value
	misshit_lab = {} ## misshit labels
	miss_index = {}  ## misshit index
	hit_val = {} ## hit value
	hit_lab = {} ## hit labels
	hit_index = {}  ## hit index

	corr_misshit_lab = {}  ## corrected misshit labels
	corr_misshit_val = {}  ## corrected misshit value

	corr_hit_lab = {} ## corrected hit labels, matching labels of only hits
	corr_hit_val = {} ## corrected hit val, matching values of hit labels only

	sumbad = {} ## sum of corrected misshits
	badlab = {}
	sumhit = {}
	hitlab = {}
	sumhit[cat] = []
	hitlab[cat] = []
	sumbad[cat] = []
	badlab[cat] = []
	is_match = []
	newhits = {}
	new_misshits = {}
	has_fp = fpcount = fpval = fpmin = 0 
	print "IN EVALUATE FUNCTION"	
	writer.writerow(["Evaluate function:"])
	writer.writerow(["iteration:",iteration])

#	print "Misshits:",miss_hits

	########### H A N D L I N G  M I S S H I T S ###########

	######## MISS HIT EXEMPLAR #########

	miss_exemplar,miss_thresh,m_hits,m_misshits = handle_misshits(miss_hits,hits,val,ref,cat,writer,model,has_fp,fpmin,iteration)
		########### CHECK THE NEW EXEMPLAR AND THRESHOLD FOR FP ################
        has_fp,fpcount,fp_labels,fpval,fpmin = check_fp(cat,miss_exemplar,miss_thresh,writer)
	if(has_fp):
		print "FP found in misshits"
	if(len(m_misshits)>0):
		print "misshits found"
	while(has_fp or len(m_misshits)>0):
	        miss_exemplar,miss_thresh,m_hits,m_misshits = handle_misshits(m_misshits,m_hits,val,ref,cat,writer,model,has_fp,fpmin,iteration)
#	        model[cat].append([miss_exemplar,miss_thresh])
        	########### CHECK THE NEW EXEMPLAR AND THRESHOLD FOR FP ################
	        has_fp,fpcount,fp_labels,fpval,fpmin = check_fp(cat,miss_exemplar,miss_thresh,writer)
		if(has_fp):
			print "FP found in misshits"
		if(len(m_misshits)>0):
			print "misshits found"

	print "NO MORE MISSHITS FOUND"
	print "before model:",model[cat]
	for key,value in model.iteritems():
		for exemplar in value:
			if exemplar[0] == miss_exemplar: ## replace if same exemplar label with new thresh
				exemplar[0] = miss_exemplar
				exemplar[1] = miss_thresh
		if key == cat:
			if [miss_exemplar,miss_thresh] not in value:
#				print "model value:",value
				if miss_thresh < 0.1:
					miss_thresh = 0.2
				model[cat].append([miss_exemplar,miss_thresh]) ## append resulting exemplar and threshold to the model and write it to result file
				print miss_exemplar
				print "APPEND MODEL IN missHITS"


	print "model:",model[cat]

	########### H A N D L I N G  H I T S ############

#	if(has_fp): ## hits,hit_val,hit_lab,hit_index,corr_hit_lab,corr_hit_val
	########## Now for Exemplar calculations ##############

	######## HIT EXEMPLAR #########
	
	hit_exemplar,hit_thresh,h_hits,h_misshits = handle_hits(miss_hits,hits,val,ref,cat,writer,model,has_fp,fpmin,iteration)
        ########### CHECK THE NEW EXEMPLAR AND THRESHOLD FOR FP ################
        has_fp,fpcount,fp_labels,fpval,fpmin = check_fp(cat,hit_exemplar,hit_thresh,writer)
	if(has_fp):
		print "FP found in hits"
	if(len(h_misshits)>0):
		print "misshits found"

	while(has_fp or len(h_misshits)>0):
		hit_exemplar,hit_thresh,h_hits,h_misshits = handle_hits(h_misshits,h_hits,val,ref,cat,writer,model,has_fp,fpmin,iteration)
#		model[cat].append([hit_exemplar,hit_thresh])
		########### CHECK THE NEW EXEMPLAR AND THRESHOLD FOR FP ################
	        has_fp,fpcount,fp_labels,fpval,fpmin = check_fp(cat,hit_exemplar,hit_thresh,writer)
		if(has_fp):
			print "FP found in hits"
		if(len(h_misshits)>0):
			print "misshits found"

	print "NO MORE MISSHITS IN HITS"
	for key,value in model.iteritems():
		for exemplar in value:
			if exemplar[0] == hit_exemplar: ## replace if same exemplar label with new thresh
				exemplar[0] = hit_exemplar
				exemplar[1] = hit_thresh
		if key == cat:
			if [hit_exemplar,hit_thresh] not in value:
				print "APPEND MODEL IN HITS"
				if hit_thresh < 0.1:
					hit_thresh = 0.2
				model[cat].append([hit_exemplar,hit_thresh]) ## append exemplar and thresh to model and write it to result file
	
	writer.writerow(model[cat]) ## write the model to the result file
#	writer.writerow(model[cat]) ## write the model to the result file

	return model

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

## Run shell script on this dir to create a distance matrix, which will be the new fname
resultdir = "/home/fimz/Dev/datasets/500-results/rev/novelty"  ## result directory path
os.system("python rev-combncdspam.py --sigdir /home/fimz/Dev/datasets/balanced-raw/imbalanced-100 --datdir /home/fimz/Dev/datasets/balanced-raw/imbalanced-100 --iter 1 --outdir "+resultdir)
os.system("mv /home/fimz/Dev/scripts/output/* "+resultdir)

#fname = sys.argv[1] ## take score file as input
fname = open("result.file",'r').read()
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
#	   writer.writerow([cat,"(Labels,Scores)",','.join(map(str,ref[cat])).strip("[]")])
#	   writer.writerow([cat,"Minimum:",','.join(map(str,minres[cat])).strip("[]")])
	   for i in range(len(ref[cat])):
		   if ref[cat][i][1] == min(sums[cat]): ## if minimum value in list is same as current cat
#			   print ref[cat][i]  ## label and its min value pair
			   writer.writerow(["(Exemplar-Label,Min)",ref[cat][i]])
			   writer.writerow(["Max Threshold",max(val[ref[cat][i][0]]) ])
			   writer.writerow(["Matching Labels:"])
			   writer.writerow(match_labels[ref[cat][i][0]]) ## write matching labels per exemplar
			   writer.writerow(["Matching similarity scores:"])
	   	           writer.writerow(match_score[ref[cat][i][0]]) ## write score of these labels per exemplar
			   model[cat] = []  ## create model
			   model[cat].append([ref[cat][i][0],max(val[ref[cat][i][0]])]) ## model with exemplar and threshold pair
			   ### E X E M P L A R S ###
			   exemplar_lab = ref[cat][i][0] ## Exemplar label
			   exemplar_val = val[ref[cat][i][0]][:] ## Exemplar value
			   exemplar_thresh = max(val[ref[cat][i][0]])
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
			     
			     for myscore in val[exemplar_lab]:
				if myscore < 0.85: ## Sanity threshold changed for NCD and spsum
	# 				   print myscore
					   sane.append(myscore)
					   count = count + 1
				else:
					outlier_lab[exemplar_lab].append(val[exemplar_lab])
					outlier_val[exemplar_lab].append(val[exemplar_lab])

				if myscore < fpmin: ## for split thresh
					temp.append(myscore)
			     
			     y1 = numpy.median(sane)  ## Replace avg with median for all values
			     #split_thresh = math.fabs(fpmin - y1)/2.0## the threshold required to split data into groups
			     split_thresh = max(temp)

			     for j in range(len(val[exemplar_lab])):
				y2 = val[exemplar_lab][j]
				x1 = x2 = 0
				p1 = [x1,y1]
				p2 = [x2,y2]
				if ( (y2 <= split_thresh and y2 < 0.85) or (y2 < 0.4) ):  ## Match if eucl dist is below 1.95
	#					print match_labels[ref[cat][i][0]][j]
	#					print i,j
					matches[exemplar_lab].append(match_labels[exemplar_lab][j]) ## Append labels of matching criteria of eucl distance of < 0.85
					if exemplar_lab in hits:
						hits[exemplar_lab].append(match_labels[exemplar_lab][j]) ## append results to hits dictionary
					else:
						hits[exemplar_lab] = [] ## create new dictionary key
						hits[exemplar_lab].append(match_labels[exemplar_lab][j]) ## append results tohits dictionary
				else:
					matches[exemplar_lab].append("MISS-HITS") ## Did not match
					if exemplar_lab in miss_hits:
						 miss_hits[exemplar_lab].append(match_labels[exemplar_lab][j]) ## Did not match
					else:
						miss_hits[exemplar_lab] = []
						miss_hits[exemplar_lab].append(match_labels[exemplar_lab][j]) ## Did not match
			     			     			     			   

#			     writer.writerow(["Euclidean Distance"])
#			     writer.writerow([ euc_dist( [j,y1],[j,val[exemplar_lab][j]]) for j in range(len(val[exemplar_lab])) ])

#			     writer.writerow(["Median",y1])
#			     writer.writerow([y1])
			     writer.writerow(["split threshold",split_thresh])
#			     writer.writerow([split_thresh])
			     writer.writerow(["Matching label after euclid"])
			     writer.writerow(matches[exemplar_lab])
			     new_thresh = float(split_thresh) ## should be the max of values under fpmin 
			     if exemplar_lab in miss_hits:
                                        writer.writerow(["Missmatch Labels"])
                                        writer.writerow(miss_hits[exemplar_lab])
                                        writer.writerow(["Count Missmatch labels",len(miss_hits[exemplar_lab])])
					#writer.writerow([len(miss_hits[exemplar_lab])])
			     ## Changes to Model ##
			     model.pop(cat)
			     model[cat] = []
   			     writer.writerow(["Model Revised in FP:"])
			     model[cat].append([exemplar_lab,new_thresh])
			     writer.writerow(model[cat])
			     
			     ## Call the evaluate_model function ## 
#			     print "match_score:",match_score
#			     print "match_label:",match_labels
#			     new_misshits,newhits,model = evaluate_model(miss_hits[exemplar_lab],match_score,match_labels,cat,writer,model,has_fp,fpmin,iteration)
			     print "Exemplar: ",exemplar_lab
			     print "Threshold: ",new_thresh
			     new_misshits = miss_hits[exemplar_lab][:]
			     new_hits = hits[exemplar_lab][:]
#			     while(len(new_misshits) > 0): ## recall the evaluate_model funct till there are no more misshits ##
 			     iteration = iteration + 1
			     print "New misshits:",new_misshits
			     model = evaluate_model(new_misshits,new_hits,match_score,match_labels,cat,writer,model,has_fp,fpmin,iteration)
			   	   
			   else: ## NO FP found
				   print "NO FP FOUND !!!"
				   for key,value in model.iteritems():
						for exemplar in value:
							if exemplar[0] == exemplar_lab: ## replace if same exemplar label with new thresh
								exemplar[0] = exemplar_lab
								if exemplar_thresh < 0.1:
									exemplar_thresh = 0.2
								exemplar[1] = exemplar_thresh
						if key == cat:
							if [exemplar_lab,exemplar_thresh] not in value:
								print "APPEND MODEL IN HITS"
								if exemplar_thresh < 0.1:
									exemplar_thresh = 0.2
									model[cat].append([exemplar_lab,exemplar_thresh]) ## append exemplar and thresh to model and write it to result file
				   writer.writerow(["MODEL WHEN NO FP: ",model[cat]])
   except ValueError:
	   print "ValueError occured for cat:",cat

writer.writerow(["Model(Median Exemplar, Max Threshold)"])
for cat in topLevelCategories:
   t = []
   x = []
   y = []
   try:
#	writer.writerow(model[cat])
	t = maxt[cat][:]
	print t
#:	writer.writerow(t)
	y = val[t[0]][:]
	x = range(0,len(y))
#	x = match_labels[t[0]][:]
	plot_scat(x,y,t[0])
   except KeyError:
	   print "Key Error:",cat

f = open("mymodel.txt",'w')
for cat in topLevelCategories:
	if cat in model:
		writer.writerow(["category: ",cat])
		writer.writerow(["signatures in model: ",len(model[cat])])
		writer.writerow(model[cat])
		for item in model[cat]:
#			print type(item)
#			data = item.strip("[]")
			f.write(item[0]+","+str(item[1])+"\n")
			print "model:",item

#os.system("mv matrix.csv ../datasets/500-results/rev/imbalanced-100/ ; mv *.png ../datasets/500-results/rev/imbalanced-100/") ## MOVE RESULTS TO RESULT FOLDER
