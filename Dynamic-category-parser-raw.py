# One possible way to carve up Fahim's ROC data files
# by Giovanni July 27, 2011
# Editted by Fahim 20110728
# Usage:
# $ python Dynamic-category-parser.py /path/to/ncd-result.txt numeric-metric-value 
# $ mv *-500-dyn-result-6* /path/to/target
#
import sys  ##  For grabbing input from SHELL
import math ##  For sqrt()
import time ##  For unique output file name creation
import pylab ## mathplotlib
import scipy ## scipy
import numpy
from numpy import *
import math
#==========================
def lookuplist(label):
#=========================
        if not labellist:
                labellist.append(label)
#       for labels in labellist:
        if label in labellist:
                1
        else:
                labellist.append(label)
        return labellist
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
    
    part1, part2, value = line.split()           # Split the three parts of the line
    part1Class, part1Details = part1.split("-")  # split the first and second headers at the "-" to extract class
    part2Class, part2Details = part2.split("-")
    category1 = categorisePayload(part1Class, categories)           # Classify the header -> return 14 for 14.1, 14.1.1, 14.1.2
    category2 = categorisePayload(part2Class, categories)
    # Make sure both headers are recognised
    assert category1 is not None, "Line #" + str(lineNo) +" - Can't find " + str(category1) + " in " + str(line)
    assert category1 is not None, "Line #" + str(lineNo) + " - Can't find " + str(category1) + " in " + str(line)
    sameCategories = (category1 == category2)

    uniqlabels = lookuplist(category1)    
#    print "Line ",lineNo, ": ", line, " >>>> ", category1, category2, str(sameCategories).upper()
#    print type(line)
#    print value
    # NOW DO SOMETHING :-)
    if sameCategories:                   # Increment Correct classification count
## Added by fahim: test for threshold
#	combcounter = combcounter + 1
	if float(value) < thresh:
	        categoryMatches[category1] = categoryMatches[category1] + 1;  ## Increment TP counter for this category X if both labels same, and score below threshold
#	        categoryMatches[category2] = categoryMatches[category2] + 1;
        else:
		categoryFN[category1] = categoryFN[category1] + 1; ## FN counter (further need to apply check that whether 1of this matched withsame cat). Same cat but above thresh 
    else:
	if float(value) < thresh:
		categoryFP[category1] = categoryFP[category1] + 1; ## FP counter (diff labels but score below threshold)
	if (float(value) > thresh):  ## TN Test Added by Fahim on 20110824. Diff category and above thres i.e. true rejection
		categoryTN[category1] = categoryTN[category1] + 1;

    categoryCount[category1] = categoryCount[category1] +1 ;                  # Total Count  # Required only for cat X
 #   categoryCount[category2] = categoryCount[category2] +1;
    return sameCategories
    
#===============================================================================
def resetMatchCounts(topLevelCategories):
#===============================================================================
    """
    Reset two arrays that maintain the counts of what matched and the total 
    number of tests for each category to zero. Actually they're dictionaries
    """
    global categoryCount, categoryMatches, categoryFP, categoryFN
    for cat in topLevelCategories:         # Initialise an array of counts
        categoryCount[cat] = 0
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
    samesum = 0;
    expectedTP = 0;
    totalcomb = 0;
    totalstreams = 0;
    global optimized;
    global counter;
    accuracy = 0;
    f = open(filename, "r");
#    out = open(output, 'a')
    for line in f:
        line = line[:-1]
        lineNo = lineNo+1
        same = classifyAttack(line, categories, lineNo)  # Same Class?
#    result = []         
    # When finished, display the counts
    print "\nRESULTS:"
    res = []	
## Calculate sum of total number of combinations per category
    for cat in topLevelCategories:
	totalcomb = totalcomb + int(categoryCount[cat])

    print "Total Comb: ",totalcomb
    totalstreams =  math.sqrt(totalcomb)
    print "Total Streams: ",totalstreams

    for cat in topLevelCategories:
	expectedTP = expectedTP + (int(categoryCount[cat]/totalstreams) * int(categoryCount[cat]/totalstreams))
	totalFP = totalFP + int(categoryFP[cat])
	totalTP = totalTP + int(categoryMatches[cat])
	totalTN = totalTN + int(categoryTN[cat])
	totalFN = totalFN + int(categoryFN[cat])
	samesum = samesum + (int(categoryCount[cat]/totalstreams) * int(categoryCount[cat]/totalstreams))
	res.append( str(thresh) + ","+ cat + "," + str(categoryCount[cat]) + "," + str(categoryCount[cat]/totalstreams) + "," + str(int(categoryCount[cat]/totalstreams) * int(categoryCount[cat]/totalstreams)) + "," + str(categoryMatches[cat]) + "," +  str(categoryFP[cat]) +  "," + str(categoryFN[cat]) + "," + str(categoryTN[cat]) + "\n" )
#	out.write(("%s,%s,%s,%s,%s,%s,%s,%s\n")%(thresh, cat, str(categoryCount[cat]), str(categoryCount[cat]/500), int(categoryCount[cat]/500) * int(categoryCount[cat]/500), categoryMatches[cat],  categoryFP[cat], categoryFN[cat] ))
#    print "Total FP: ",totalFP
#    print "Total FN: ",totalFN
#    print "Total TP: ",totalTP
#    print "Total TN: ",totalTN
#    print "Sum of all same classes: ", samesum
#    print "TP+FN = ", totalTP + totalFN
    totalTP = totalTP + 0.0
    totalFP = totalFP + 0.0
    totalTN = totalTN + 0.0
    totalFN = totalFN + 0.0
    TPperc = (totalTP/expectedTP)*100
    FPperc = (totalFP/(totalTP+totalFP+totalTN+totalFN))*100
#===================
# TPR = TP/P
# FPR = FP/N
#===================
    tpr = totalTP/(totalTP + totalFN)
    if totalFP > 0:
	    fpr = totalFP/(totalFP + totalTN)
    else:
	    fpr = 0.0
#========================
# Accuracy = (TP=TN)/P+N
# AUC = (1+TPR-FPR)/2
#========================
    accuracy = (totalTP + totalTN)/( (totalTP+totalFN) + (totalFP + totalTN) )
    auc = (1.0 + tpr - fpr)/2

#=========================================
# Create a list of optimized[maxrow][10] results
#========================================
#    maxACC = max(accuracy)
#    maxAUC = max(auc)
#    optimized[maxrow][10]index = auc.index(max(auc))


#    print "TPR = Total TP / Total TP+FN = ", tpr
 #   print "FPR = Total FP / Total FP+TN = ", fpr	
 #   print "Accuracy = ",accuracy
 #   print "AUC = ",auc

    res.append(',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + str(tpr) + "," + str(fpr) + "," + str(accuracy) + "," + str(auc))

    rates.append( str(totalTN) + ',' + str(totalFN)+ ',' + str(thresh) + ',' + str(totalTP) + ',' + str(totalFP) + ',' + str(TPperc) + ',' + str(FPperc) + ',' +  str(tpr) + "," + str(fpr) + "," + str(accuracy) + "," + str(auc) + '\n')

    optimized = numpy.insert(optimized,counter,numpy.array(( totalTN,totalFN,thresh,totalTP,totalFP,TPperc,FPperc,tpr,fpr,accuracy,auc)),0)

    print "Counter: ",counter
    print "Values: ",optimized[counter]
#    print res
#    print ''.join(res)
    out.write(''.join(res) + "\n")
    out.close()
    x_list.append(fpr)
    y_list.append(tpr)
	

#	print ": Total Streams =", sqrt(int(str(categoryCount[cat]).ljust(6)))
#	out.writelines(("%s,%s,%s,%s,%s,%s\n") % (thresh, cat,  str(categoryCount[cat]).ljust(6),  categoryMatches[cat], categoryFP[cat],  categoryFN[cat]))
#	out.writelines(("%s,%s,%s,%s,%s\n") % (thresh, str(categoryCount[cat]).ljust(6),  categoryMatches[cat], categoryFP[cat],  categoryFN[cat]))
#	result[] = 
#    print categoryMatches
#    print categoryCount
#    print uniqlabels
#    print labellist
#    out.close()
#===============================================================================
# Main Program starts here    
categories, topLevelCategories = loadCategories("categories-500.txt")
# print categories
#dumpCategories(categories, topLevelCategories)  # can be commented out - diagnostic only - show the categories 
uniqlabels = []
labellist = []
categoryCount   = {}
categoryMatches = {}
categoryFP = {}
categoryFN = {}
categoryTN = {}
x_list = []
y_list = []
rates = []
optimized = numpy.zeros((40,11))
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
infile = sys.argv[1]
metric = sys.argv[2]
output = "%s-500-dyn-result"%int(time.time())
output = output + "-" + metric + ".csv"
print topLevelCategories
print "Threshold ," , ",".join(topLevelCategories)
header = []

#out = open(output,'w')
#out.writelines("Threshold,  TotalStreams, TotalCombinations, TP, FP, FN")
#out.close()
fname = output
out = open(fname, 'w')
out.write("Threshold, Class, Total Combinations, Pkts/Streams, Same Class combinations, TP, FP, FN, TN, TPR, FPR, Accuracy, AUC\n")
out.close()
rates.append("Summary:\n")
rates.append("TotalTN,TotalFN,Threshold,TotalTP,TotalFP,TP%,FP%,TPR,FPR,Accuracy,AUC\n")
#optimized.append("Optimum Result:\n")
#optimized.append("TotalTN,TotalFN,Threshold,TotalTP,TotalFP,TP%,FP%,TPR,FPR,Accuracy,AUC\n")
if int(metric) == 3:
	maxthresh = 2
else:
	maxthresh = 1
while(thresh < maxthresh):
	resetMatchCounts(topLevelCategories)
	out = open(fname, 'a')
#	out.close()
	processResultFile(infile, out)
	thresh = thresh + 0.05
	counter = counter + 1
#out.close
prev = 0
for row in range(40):
	newmax = optimized[row][10]
	if newmax > prev:
		prev = newmax
		maxrow = row

print "Max results: ",prev
print "Max index: ",maxrow
rates.append("\nOptimized:\n")
#rates.append(optimized[maxrow][10])
rates.append( str(optimized[maxrow][0])+ ',' + str(optimized[maxrow][1])+ ',' + str(optimized[maxrow][2]) + ',' + str(optimized[maxrow][3]) + ',' + str(optimized[maxrow][4]) + ',' + str(optimized[maxrow][5]) + ',' + str(optimized[maxrow][6]) + ',' + str(optimized[maxrow][7]) + ',' + str(optimized[maxrow][8]) + ',' + str(optimized[maxrow][9]) + ',' + str(optimized[maxrow][10]) )
out = open(fname, 'a')
out.write(''.join(rates) + "\n")
out.close()
# ##########################
# Define Axes and plot graph
# ##########################
pylab.xlabel("FPR")
pylab.ylabel("TPR")
#pylab.axis(-1,1,-1,1)
print "Metric: ", metric
#print "Type: ", type(metric)
if int(metric) == 1:
	pylab.title("NCD")
	print "In NCD"
if int(metric) == 2:
	pylab.title("SPAMSUM")
	print "In spamsum"
if int(metric) == 3:
	pylab.title("COMBINED")
	print "In COMBINED"

pylab.plot(x_list, y_list, 'r')
pylab.xticks(scipy.arange(0,1.01,0.1))
pylab.yticks(scipy.arange(0,1.01,0.1))

pylab.ylim(ymin = 0, ymax = 1.01)
pylab.xlim(xmin=-.025, xmax = 1.01)
#pylab.ylim(ymin=-.025, ymax = 1.01)
#fig, ax = pyplot.subplot()
#pylab.xaxis.set_major_locator(MultipleLocator(0.1))
#fig = pylab.figure()
#ax = fig.add_subplot(1,1,1)
#ax.plot(x_list, y_list, 'r')
#ax.set_xticks(scipy.arange(-0.25,1.01, 0.1))
#fig.show()
## Save plot as PNG
pylab.grid(True)
pylab.savefig(fname + '.png')
