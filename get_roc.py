# One possible way to carve up Fahim's ROC data files
# by Giovanni July 27, 2011
# Editted by Fahim 20110728
# Usage:
# $ python Dynamic-category-parser.py /path/to/ncd-result.txt numeric-metric-value 
# $ mv *-500-dyn-result-6* /path/to/target
#python Dynamic-category-parser-composite.py /home/fimz/Dev/datasets/500-results/rev/imbalanced-100/1327628422-newcombined-out.txt 3; mv *-500-dyn-result* /home/fimz/Dev/datasets/500-results/rev/imbalanced-100/;mv output/* /home/fimz/Dev/datasets/500-results/rev/imbalanced-100/
#########
# Usage:#
#########
# python get_roc.py /home/fimz/Dev/datasets/500-results/rev/test-2/1334196595-newcombined-out.txt 3 /home/fimz/Dev/datasets/500-results/rev/test-2
#
#!/usr/bin/python
import sys  ##  For grabbing input from SHELL
import math ##  For sqrt()
import time ##  For unique output file name creation
import pylab ## mathplotlib
import scipy ## scipy
import numpy
from numpy import *
import math
import os ## for all os commands
import pickle
#==========================
def hitUniq(row):
#==========================
## Create a list of unique hits TP and FP in the form cat1, cat2, score
   global hits

   if not hits:
        hits.append(row)
#   for row in hits:
   if row in hits:
            1
   else:
        hits.append(row)
#	print "\nrow: ", 
#   print "\nLenght of hits: ", len(hits)
#        return labellist1, labellist2


#==========================
def countUniq(u1,u2):
#==========================

	global u1categoryCount, u2categoryCount

	for label in u1:
	    part1Class, part1Details = label.split("-")  # split the first and second headers at the "-" to extract class
	    category1 = categorisePayload(part1Class, categories)           # Classify the header -> return 14 for 14.1, 14.1.1, 14.1.2
	    # Make sure both headers are recognised
	    assert category1 is not None, "Line #" + str(lineNo) +" - Can't find " + str(category1) + " in " + str(line)
	    u1categoryCount[category1] = u1categoryCount[category1] +1 ;                  # Total Count  # Required only for cat X

	for label in u2:
	    part2Class, part2Details = label.split("-")
	    category2 = categorisePayload(part2Class, categories)
	    assert category2 is not None, "Line #" + str(lineNo) + " - Can't find " + str(category2) + " in " + str(line)
	    u2categoryCount[category2] = u2categoryCount[category2] +1 ;                  # Total Count  # Required only for cat Y

#==========================
def lookuplist(label1,label2):
#==========================
        if not labellist1:
                labellist1.append(label1)
        if not labellist2:
                labellist2.append(label2)

#       for labels in labellist:
        if label1 in labellist1:
                1
        else:
                labellist1.append(label1)
        if label2 in labellist2:
                1
        else:
                labellist2.append(label2)

        return labellist1, labellist2
#===============================================================================
def loadCategories (filename):
#===============================================================================
    """Load a category file and return a list of lists.
       The category file has one class of exploits per line and uses :: between the items
        e.g.
            5 :: Remote Framebuffer VNC Exploits :: 5.1.1 :: 5.1.2 :: 5.2 :: 5.3
           29 :: POP3 Login Attempt
        
        Each line is turned into a list:      
          - The first item is the value to return if this class matches (e.g. 14 for 14.1.1, 14.1.2 ...)
          - the second item is the values to be tested (those like the 14.1.1 or 18 above)
          - the third is the description of this class of attack/payload ...
        If there is only one item to test (like the 29 above, the first and second items are the same:
        The above pair of lines should return:
         [ [ '5', ['5.1.1', '5.1.2', '5.2', '5.3'], " Remote Framebuffer VNC Exploits"], 
           [ '29',['29'], 'POP3 Login Attempt'] 
         ]
        IMPORTANT: 
            The items in the list are all strings, even if they look like numbers. This means that a 
            category file like this is fine (even though it makes no sense):
            
              webstuff    :: Web browswer related stuff :: http :: https :: GET :: POST
              fileTranfer :: File transfer related      :: ftp :: scp :: rcp
            
            As it's written, the capitalisation must match when testing the list items    
    """
    categories = []
    topLevelCategories = []    # These are the result categories like 14, 15, 18, 29.1 is 
    f = open(filename, "r");
    for line in f:
        if line == "": continue        # ignore blank lines
        fields = line.split("::")
        fields = [ item.strip() for item in fields]     # trim leading and trailing spaces
        fieldCount = len(fields)
        assert fieldCount >= 2, "Line has less than two fields: " + line
        description = fields[1]
        if fieldCount == 2:           # No subclasses, so if first value matches return it   
          returnValue = fields[0]
          testValues    = fields[0:1]  # Make sure the test values are a list, even if only a single item
        else:
          returnValue = fields[0]
          testValues    = fields[2:]  # All fields after the description are test values
        testVector = [returnValue, testValues, description]   
        # print testVector
        categories.append(testVector)
        topLevelCategories.append(returnValue)
    return categories, topLevelCategories
        
        
#===============================================================================
def dumpCategories(categoryList, topLevelCategories):
#===============================================================================
    """ Display the list of categories for easy reading and checking"""
    print "Dump of the parsed Category tests"    
    for category in categoryList:
        print "\nDescription: ", category[2]
        print "    ", category[1] , "===>>> ", category[0]
    print "\nTop Level (result class) categories:"
    print "   ", topLevelCategories

#===============================================================================
def categorisePayload(header, categories):
#===============================================================================
    " find what a header (e.g. 14.1.2), matches (i.e. 14) and return it "
    for vector in categories:
        if header in vector[1]: 
           return vector[0]
    return None      # This should never happen, it's checked later 

r = {}

#===============================================================================
def classifyAttack(line, categories, lineNo):
#===============================================================================
    """ 
    For the given line from the data file, which is of the form: 
       
      14.1.1-f6e5e49ee210d52a2.fuzz 18-05568905b723efc.fuzz 0.875
    
    split it into the the components "14.1.1",  "18", and "0.875", and then see if 
    the first two are in the same class (after the "14.1.1" has been recognised as
    belonging to the "14" class.
    
    IMPORTANT: This routine assumes the part that should match is terminated with a "-"
    """
    global uniq1
    global uniq2
    global tphitHistory, fphitHistory, tnhitHistory, fnhitHistory, classified, outlier
#    global thresh
    part1, part2, value = line.split()           # Split the three parts of the line
    part1Class, part1Details = part1.split("-")  # split the first and second headers at the "-" to extract class
    part2Class, part2Details = part2.split("-")
    category1 = categorisePayload(part1Class, categories)           # Classify the header -> return 14 for 14.1, 14.1.1, 14.1.2
    category2 = categorisePayload(part2Class, categories)
    # Make sure both headers are recognised
    assert category1 is not None, "Line #" + str(lineNo) +" - Can't find " + str(category1) + " in " + str(line)
    assert category2 is not None, "Line #" + str(lineNo) + " - Can't find " + str(category2) + " in " + str(line)
    sameCategories = (category1 == category2)
## Added by Fahim to account for signature and dataset lists ##
    uniq1,uniq2 = lookuplist(part1,part2)    
#    print "Line ",lineNo, ": ", line, " >>>> ", category1, category2, str(sameCategories).upper()
#    print type(line)
#    print valu
    
    determine_fn = 0
#    print "Model len: ",len(model)
#=================================================================================
# TP, FP, TN, FN CALCULATIONS
#=================================================================================
    # NOW DO SOMETHING :-)
#    for item in model:
#	    print item
    if sameCategories or "X" in part1:                   # Increment Correct classification count
## Added by fahim: test for threshold
#	combcounter = combcounter + 1
	## Get threshold specific to signature class ##
        model = get_thresh(category2)
	for item in model:
	
	   if part2 == item[0]: ## get the model for the exemplar. now get its threshold
#		print "GOTCHA"   
		
		if float(value) <= float(item[1])+0.005: ## adding lessthan or equals to, to support the model
			if category1 == "X":
				category1 = category2
			classified.add(str(part1))  ## labels that got classified

			if category1 in tphitHistory and part1 not in tphitHistory[category1]:
				tphitHistory[part2].append(str(part1))  ## add it to the history list
				categoryMatches[category1] = categoryMatches[category1] + 1;  ## Increment TP counter for this category X if both labels same, and score below threshold

			if category1 not in tphitHistory:
				tphitHistory[part2] = []
				categoryMatches[category1] = categoryMatches[category1] + 1;  ## Increment TP counter for this category X if both labels same, and score below threshold
				tphitHistory[part2].append(str(part1))  ## add it to the history list
			
			if part1 in tphitHistory:
				tphitHistory[part2].append(str(part2))
			if part1 not in tphitHistory:  ## If the sample has not been previously seen/hit by the class
				tphitHistory[part2] = []
				tphitHistory[part2].append(str(part2))  ## add it to the history list
			### adding per signature support ###
			if item[0] in tphitHistory:
				tphitHistory[item[0]].append(part1)
		else: ## FN

			outlier.add(str(part1))  ## labels that did not get classified
			try:
				if category1 in fnhitHistory:
					if part1 not in fnhitHistory[category1]:
						if category1 in tphitHistory:
								if part1 not in tphitHistory[category1]:
									fnhitHistory[category1].append(str(part1))  ## add it to the history list
									categoryFN[category1] = categoryFN[category1] + 1; ## FN counter (further need to apply check that whether 1of this matched withsame cat). Same cat but above thresh
									print "FN Sample:", part1
									print "FN cat: ", category1
						if category1 not in tphitHistory:
		    	                              		        fnhitHistory[category1].append(str(part1))  ## add it to the history list
                                                                        categoryFN[category1] = categoryFN[category1] + 1; ## FN counter (further need to apply check that whether 1of this matched withsame cat). Same cat but above thresh


				if category1 not in fnhitHistory:
					fnhitHistory[category1] = []
					if category1 in tphitHistory:
						if part1 not in tphitHistory[category1]:
							fnhitHistory[category1].append(str(part1))  ## add it to the history list
							categoryFN[category1] = categoryFN[category1] + 1; ## FN counter (further need to apply check that whether 1of this matched withsame cat). Same cat but above thresh
							print "FN Sample:", part1
							print "FN cat: ", category1
					if category1 not in tphitHistory:
                                                      fnhitHistory[category1].append(str(part1))  ## add it to the history list
                                                      categoryFN[category1] = categoryFN[category1] + 1; ## FN counter (further need to apply check that whether 1of this matched withsame cat). Same cat but above th
					
				if part1 not in fnhitHistory:  ## If the sample has not been previously seen/hit by the class
					fnhitHistory[part1] = []
					fnhitHistory[part1].append(str(part2)+","+str(value))  ## add it to the history list
			except KeyError:
				1	

		try:
			if part1 in fnhitHistory[category1] and part1 in tphitHistory[category1]:
				print "Common items in FN:",part1
				fnhitHistory[category1].remove(part1)
		except KeyError:
			1
		
    else:  ## Both categories not same
	check_novel = get_thresh(category1)    ## check novel categories not in model
	if check_novel == 0:
#		myfile = open("novel-labels.txt",'a')
		outlier.add(str(part1))  ## labels that were not in the model
#		myfile.write(str(part1))
#		myfile.close()

	## Get threshold specific to signature class ##
        model = get_thresh(category2)
	for item in model:
	  if part2 == item[0]: ## confirm if its the exemplar, then fetch the threshold
	    if float(value) <= float(item[1]): ## FP
#		print "part1: ",part1
#		print "part2: ",part2
#		print "model:",model
		print "XXXXXXXXXXXXXX FOUND A FP XXXXXXXXXXXXXX"		
		if category2 in fphitHistory and part1 not in fphitHistory[category2]:
			fphitHistory[category2].append(str(part1))  ## add it to the history list
			categoryFP[category2] = categoryFP[category2] + 1; ## FP counter (diff labels but score below threshold)

		if category2 not in fphitHistory:
			fphitHistory[category2] = []
			fphitHistory[category2].append(str(part1))  ## add it to the history list
			categoryFP[category2] = categoryFP[category2] + 1; ## FP counter (diff labels but score below threshold)

		if part1 in fphitHistory:
			fphitHistory[part1].append(str(part2))  ## add it to the history list	
		if part1 not in fphitHistory:  ## If the sample has not been previously seen/hit
			fphitHistory[part1] = []
			fphitHistory[part1].append(str(part2))  ## add it to the history list

#		hitUniq(line)
	    if float(value) > float(item[1]):  ## TN Test Added by Fahim on 20110824. Diff category and above thres i.e. true rejection
#		categoryTN[category1] = categoryTN[category1] + 1;
#		print "YAY FOUND A TN"
		if category2 in tnhitHistory and part1 not in tnhitHistory[category2]:
#			if part1 not in fphitHistory[category1]:
			tnhitHistory[category2].append(str(part1))  ## add it to the history list
			categoryTN[category1] = categoryTN[category1] + 1;

		if category2 not in tnhitHistory:
			tnhitHistory[category2] = []
			tnhitHistory[category2].append(str(part1))  ## add it to the history list
			categoryTN[category1] = categoryTN[category1] + 1;
	
		if part1 in tnhitHistory:
			tnhitHistory[part1].append(str(part2)+","+str(value))  ## add it to the history list	
#			tnhitHistory[category1].append(str(part2)+","+str(value))  ## add it to the history list	
		if part1 not in tnhitHistory:
			tnhitHistory[part1] = []
			tnhitHistory[part1].append(str(part2)+","+str(value))  ## add it to the history list
#			tnhitHistory[category1] = []
#			tnhitHistory[category1].append(str(part2)+","+str(value))  ## add it to the history list

    outlier = outlier - classified.intersection(outlier)
    categoryCount[category1] = categoryCount[category1] + 1 ;                  # Total Count  # Required only for cat X
#    categoryCount[category2] = categoryCount[category2] +1;
    return sameCategories
    
#===============================================================================
def resetMatchCounts(topLevelCategories):
#===============================================================================
    """
    Reset two arrays that maintain the counts of what matched and the total 
    number of tests for each category to zero. Actually they're dictionaries
    """
    global categoryCount, categoryMatches, categoryFP, categoryFN, u1categoryCount, u2categoryCount
    for cat in topLevelCategories:         # Initialise an array of counts
        categoryCount[cat] = 0
	u1categoryCount[cat] = 0
	u2categoryCount[cat] = 0
	categoryMatches[cat] = 0
	categoryFP[cat] = 0
	categoryFN[cat] = 0
	categoryTN[cat] = 0
	totalFP = 0
	totalTN = 0
    
#===============================================================================
def processResultFile(filename, out):
#===============================================================================
    lineNo = 0;
    totalFP = 0;
    totalTP = 0;
    totalTN = 0;
    totalFN = 0;
    tprcat = 0.0;
    fprcat = 0.0
    acccat = 0.0;
    auccat = 0.0;
    samesum = 0;
    expectedTP = 0;
    totalcomb = 0;
    totalstreams = 0;
    global perclassdict;
    global optimized;
    global counter;
    global uniq1;
    global uniq2;
    global u1categoryCount, u2categoryCount
    global thresh;
    global tphitHistory, fphitHistory, tnhitHistory, fnhitHistory
    global tphit_list, tnhit_list, fphit_list,fnhit_list
    global x_list, y_list
    global outlier,classified
    accuracy = 0;
    f = open(filename, "r");
#    out = open(output, 'a')
    for line in f:
        line = line[:-1]
        lineNo = lineNo+1
        same = classifyAttack(line, categories, lineNo)  # Same Class? call to main classify function
    f.close()

    f = open(filename, "r");
    for lin in f:  
#	print lin
	lin = lin[:-1]
	data,sig,t = lin.split()
#	print "data: ",data
	if data in uniqueData:
		0
	else:
		uniqueData.append(data) ## Create a list of unique dataset samples
    print "Unique labels=",len(uniqueData)

#    result = []         
    # When finished, display the counts
    print "\nRESULTS:"
    res = []	
## Calculate sum of total number of combinations per category
    for cat in topLevelCategories:
	totalcomb = totalcomb + int(categoryCount[cat])
    countUniq(uniq1,uniq2)
    print "Total Comb: ",totalcomb
#    totalstreams =  math.sqrt(totalcomb)
    totalstreams = len(uniq2) + len(uniq1) 
#    print "Total Streams: ",totalstreams

    for cat in topLevelCategories:
	expectedTP = expectedTP + (int(u1categoryCount[cat]) * int(u2categoryCount[cat]))
	totalFP = totalFP + int(categoryFP[cat])
	totalTP = totalTP + int(categoryMatches[cat])
	totalTN = totalTN + int(categoryTN[cat])
	totalFN = totalFN + int(categoryFN[cat])
	samesum = samesum + (int(categoryCount[cat]/totalstreams) * int(categoryCount[cat]/totalstreams))
	print "Category: ",cat
	try:
		tphit = len(tphitHistory[cat])
	except KeyError, e:
		tphit = 0;
	try:
		fphit = len(fphitHistory[cat])
	except KeyError, e:
		fphit = 0;
	try:
		tnhit = len(tnhitHistory[cat])
	except KeyError, e:
		tnhit = 0;
	try:
		fnhit = len(fnhitHistory[cat])
	except KeyError, e:
		fnhit = 0;

	print "TPcat: ", tphit
#	print "TotalTP:", totalTP
	print "FPcat: ", fphit
	print "TNcat: ", tnhit
	print "FNcat: ", fnhit
	#========
	# TPR per cat = TP/TP+FN
	# FPR per cat = FP/FP+TN
	# Accuracy per cat = (TP+TN/P+N)
	# AUC per cat = (1+TPR-FPR)/2
	#=======
#	print "category = ",cat
#	print "TP cat = ",categoryMatches[cat]
#	print "FP cat = ",categoryFP[cat]
#	print "FN cat = ",categoryFN[cat]
	try:
		tprcat = int(tphit)/(int(tphit) + int(fnhit) + 0.0 )
	except ZeroDivisionError:
		tprcat = 0.0

	if int(categoryFP[cat]) > 0:
		fprcat = int(fphit)/(int(fphit) + int(tnhit) + 0.0 )
	else:
		fprcat = 0.0
	try:
		acccat = (int(tphit) + int(tnhit) + 0.0 )/( int(tphit) + int(fnhit)  + int(fphit) +  int(tnhit) )
	except ZeroDivisionError:
		acccat = 0.0
	auccat = (1+tprcat-fprcat)/2.0
	model = get_thresh(cat) ## get the model
	print "Model:",model
#	print "type:",type(model)
	if model > 0:
		for items in model:
		   try:	
#			print "tphitHistorys:", len(tphitHistory[items[0]])  
			tphitH = len(tphitHistory[items[0]])
		   except KeyError:
			tphitH = 0
		   try:	
#			print "fphitHistorys:", len(fphitHistory[items[0]])  
			fphitH = len(fphitHistory[items[0]])
		   except KeyError:
			fphitH = 0
		   try:	
#			print "fnhitHistorys:", len(fnhitHistory[items[0]])  
			fnhitH = len(fnhitHistory[items[0]])
		   except KeyError:
			fnhitH = 0
		   try:	
#			print "tnhitHistorys:", len(tnhitHistory[items[0]])  
			tnhitH = len(tnhitHistory[items[0]])
		   except KeyError:
			tnhitH = 0

	x_list.append(fprcat) ## roc x axis
	y_list.append(tprcat) ## roc y axis

	countsig_list.append(u2categoryCount[cat])
	dataset_list.append(u1categoryCount[cat])
	tphit_list.append(tphit)
	fphit_list.append(fphit)
	fnhit_list.append(fnhit)
	tnhit_list.append(tnhit)
			      
	res.append( cat + ","+  str(u1categoryCount[cat]) + "," + str(u2categoryCount[cat]) + ","+ str(tphit) + "," +  str(fphit) +  "," + str(fnhit) + "," + str(tnhit) + "," + str(tprcat) + "," + str(fprcat) + "," + str(acccat) + "," + str(auccat) + "\n" )
#	res.append( cat + ","+ str(items[0]) + "," + str(items[1]) + ","+ str(u1categoryCount[cat]) + "," + str(u2categoryCount[cat]) + "," + str(int(categoryCount[cat])) + "," + str(int(u1categoryCount[cat] + u2categoryCount[cat])) + "," + str(int(u1categoryCount[cat] * u2categoryCount[cat]) ) + "," + str(tphitH) + "," +  str(fphitH) +  "," + str(fnhitH) + "," + str(tnhitH) + "," + str(tprcat) + "," + str(fprcat) + "," + str(acccat) + "," + str(auccat) + "\n" )

#	res.append( str(get_thresh(cat)) + ","+ cat + "," + str(u1categoryCount[cat]) + "," + str(u2categoryCount[cat]) + "," + str(int(categoryCount[cat])) + "," + str(int(u1categoryCount[cat] + u2categoryCount[cat])) + "," + str(int(u1categoryCount[cat] * u2categoryCount[cat]) ) + "," + str(categoryMatches[cat]) + "," +  str(categoryFP[cat]) +  "," + str(categoryFN[cat]) + "," + str(categoryTN[cat]) + "," + str(tprcat) + "," + str(fprcat) + "," + str(acccat) + "," + str(auccat) + "\n" )

    out.write(''.join(res) + "\n")
    out.write("Summary:")
    tnsum =  math.fabs(sum(dataset_list) - ( sum(tphit_list) + sum(fphit_list) + sum(fnhit_list) ))
    t_accuracy = ( sum(tphit_list) + sum(fphit_list) + 0.0 )/( sum(tphit_list) + sum(fphit_list) + tnsum +  sum(fnhit_list) )
    out.write(","+str(sum(dataset_list))+","+str(sum(countsig_list))+","+str(sum(tphit_list))+","+str(sum(fphit_list))+","+str(sum(fnhit_list))+","+str(tnsum)+",,,"+str(t_accuracy)+",")
    out.write("\nOutliers:\n")
    outlier = outlier - classified.intersection(outlier)
    temp_outlier = list(outlier)
#    for item in temp_outlier:
    out.write("Number of outliers found: "+str(len(temp_outlier))+"\n")
    out.write(",".join(temp_outlier))
    out.close()

    	

#============================================
# GET THRESHOLD FOR A CLASS get_thresh(class)
#===========================================
def get_thresh(testclass):
	if testclass in threshDict:
		return threshDict[testclass]
	else:
		return 0
#===========================================================
# Load optimum threshold for each class in a dict loadThresh(filename)
#===========================================================
def loadThresh(filename):
	global threshDict;
	f = open(filename,'r')
	for line in f:
		if line == "": continue  ## ignore empty lines
		line = line.strip()
		cat,t = line.split(',')
		threshDict[cat] = []
		threshDict[cat] = t

#===========================================================
# Load Model for each class in a dict loadThresh(filename)
#===========================================================
def loadModel(filename):
	global threshDict;
	f = open(filename,'r')
	for line in f:
		if line == "": continue  ## ignore empty lines
		line = line.strip()
		ex_label, ex_thresh = line.split(',')
		part1Class, part1Details = ex_label.split("-")
		categ = categorisePayload(part1Class, categories)           # Classify the header -> return 14 for 14.1, 14.1.1, 14.1.2
		if categ not in threshDict:
			threshDict[categ] = []
			threshDict[categ].append([ex_label,ex_thresh])	## Append the model to the dictionary for the category
		else:
			threshDict[categ].append([ex_label,ex_thresh])


#============================================
# DRAW ROC CURVE roc(xlist,ylist,filename)
#===========================================
def roc(xlist,ylist,filename,title,xlabel,ylabel):
	pylab.title(title)
	pylab.xlabel(xlabel)
	pylab.ylabel(ylabel)
	pylab.plot(xlist, ylist, 'r')
	pylab.xticks(scipy.arange(0,1.01,0.1))
	pylab.yticks(scipy.arange(0,1.01,0.1))
	pylab.ylim(ymin = 0, ymax = 1.01)
	pylab.xlim(xmin=-.025, xmax = 1.01)
	#fig.show()
	## Save plot as PNG
	pylab.grid(True)
	pylab.savefig(filename + '.png')
	pylab.close()

#===============================================================================
#===============================================================================
# Main Program starts here    
#===============================================================================
#===============================================================================
if __name__ == '__main__':

	os.system("rm -f *-500-dyn-result*") ## remove previous results from current dir
	categories, topLevelCategories = loadCategories("categories-500.txt") ## Load categories from cat file
	# print categories
	#dumpCategories(categories, topLevelCategories)  # can be commented out - diagnostic only - show the categories 
	uniq1 = []
	uniq2 = []
	labellist1 = []
	labellist2 = []
	hits = []
	uniqueData = []
	categoryCount   = {}
	u1categoryCount   = {}
	u2categoryCount   = {}
	categoryMatches = {}
	categoryFP = {}
	categoryFN = {}
	categoryTN = {}
	perclassdict = {}
	fphitHistory = {}
	tphitHistory = {}
	fnhitHistory = {}
	tnhitHistory = {}
	tphit_list = []
	tnhit_list = []
	fphit_list = []
	fnhit_list = []
	outlier = set()
	classified = set()
	dataset_list = [] ## total number of samples in the dataset
	countsig_list = [] ## count total number of exemplar samples
	threshDict = {}
	x_list = []
	y_list = []
	xcoord = []
	ycoord = []
	rates = []
	optimized = numpy.zeros((40,11))
	title = ""
	xlabel = ""
	ylabel = ""
	counter = 0
	thresh = 0.00
	totalFP = 0
	totalTP = 0
	totalTN = 0
	totalFN = 0
	expectedTP = 0
	TPperc = 0
	FPperc = 0
	#maxACC = 0
	#maxAUC = 0
	mx = 0
	#========================================================================
	## Command line arguments ##
#	infile = sys.argv[1]	## input result file to process
	infile = open("result.file",'r').read()
	metric = sys.argv[1]	## Metric used to determine file
	resultf = sys.argv[2]
	#threshfile = sys.argv[3] ## path to threshold file
	#========================================================================
#	loadThresh("perclassthresh.txt")	## load the threshold file and build a dictionary
	loadModel("mymodel.txt")  ## load the model. this should be a command like argument
	## Might have to change the load per threshold funct to a load the model funct.
	## The loadmodel will load the model from a file that has the model in the form of
	## labels and their threshold for each category. The model file should be a csv file where each line holds
	## a label,threshold pair. For any category there can be multiple rows of such pairs
	
	output = "%s-500-dyn-result"%int(time.time())
	output = output + "-composite-" + metric + ".csv"
	print topLevelCategories
	print "Threshold ," , ",".join(topLevelCategories)
	header = []

	#out = open(output,'w')
	#out.writelines("Threshold,  TotalStreams, TotalCombinations, TP, FP, FN")
	#out.close()
	fname = output
	out = open(fname, 'w')
	out.write("Class,  DatasetCount/category, SignatureCount/category, TP, FP, FN, TN, TPR, FPR, Accuracy, AUC\n")
	out.close()
	if int(metric) == 3:
		maxthresh = 2
	else:
		maxthresh = 1
	#======================================================
	# Create confusion matrix for optimum T
	#======================================================

	resetMatchCounts(topLevelCategories)
	out = open(fname, 'a')
	#	out.close()
	processResultFile(infile, out)  ## This is the main processing function to call
	counter = counter + 1

	#=======================================================
	# Dump TP,FP,TN,FN lists to output file #

	tnoutput = open('tnlist.pkl', 'w')
	fnoutput = open('fnlist.pkl', 'w')
	tpoutput = open('tplist.pkl', 'w')
	fpoutput = open('fplist.pkl', 'w')
	outl = open('outlier.pkl','w')

	pickle.dump(tnhitHistory, tnoutput)
	pickle.dump(tphitHistory, tpoutput)
	pickle.dump(fphitHistory, fpoutput)
	pickle.dump(fnhitHistory, fnoutput)
	pickle.dump(outlier,outl) ## dump the outlier set
	tnoutput.close()
	tpoutput.close()
	fnoutput.close()
	fpoutput.close()
	outl.close()

	# ##########################
	# Define Axes and plot graph
	# ##########################
	#pylab.xlabel("FPR")
	#pylab.ylabel("TPR")
	xlabel = "FPR"
	ylabel = "TPR"

	#pylab.axis(-1,1,-1,1)
	print "Metric: ", metric
	#print "Type: ", type(metric)
	## Copy file to output folder ##
	os.system("cp " + infile + " output/")
	fstring = infile.split("/")
	## Check Metric to add label and create graph ##
	if int(metric) == 1:
	#	pylab.title("NCD")
		title="NCD"
		print "In NCD"
	#	os.system("python ncd-fimz-graph.py " + fstring[-1]  + " " + str(optthresh) )
	#	os.system("sfdp -Tsvg output/graph-" + fstring[-1]  + " -o " + "output/" + fstring[-1] +  ".svg")
	if int(metric) == 2:
	#	pylab.title("SPAMSUM")
		title="SPAMSUM"
		print "In spamsum"

	#	os.system("python ncd-fimz-graph.py " + fstring[-1] + " " + str(optthresh) )
	#	os.system("sfdp -Tsvg output/graph-" + fstring[-1]  + " -o " + "output/" + fstring[-1] +  ".svg")

	if int(metric) == 3:
	#	pylab.title("COMBINED")
		title = "MIN(NCD,SPSUM)"
		print "In COMBINED MIN"
		print "file: ",fstring[-1]
		os.system("python create_optimized_graph.py " + fstring[-1] )

		os.system("sfdp -Tsvg output/graph-" + fstring[-1]  + " -o " + "output/" + fstring[-1] +  ".svg")
	print "xlist:",x_list
	print "ylist:",y_list
	x_list, y_list = zip(*sorted(zip(x_list, y_list)))  ## sort axis coordinates for ROC
	roc(x_list,y_list,fname,title,xlabel,ylabel)
	print "ROC created"
	os.system("mv output/* "+resultf) ## move results to result dir
	os.system("mv *-500-dyn-result* "+resultf) ## move results to result dir
#	os.system("mv matrix.csv "+resultf) ## move results to result dir

	print "RESULTS MOVED TO RESULT FOLDER"

#else __name__ == 'Dynamic-category-parser-composite': 
