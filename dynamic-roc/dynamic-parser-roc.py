######################################################################################################
#
#	Author: Fahim Abbasi
#
#	20110725
#
#	Script: Dynamic ROC calculator
#
#	Description: This script will take as input class labels to parse any result file
#	 (supplied to the infile variable) and output the number of TP and FP per lable
#
#	Usage:
#	$python dynamic-parser-roc.py classA classB classC classD ...
#	$python dynamic-parser-roc.py 10 11 12 13.1 13.2 13.3 13.4 13.5 14.1.1 14.1.2 14.5 14.6 18
#
#######################################################################################################

import csv
import sys
import re
import math

argcount = len(sys.argv)
#infile = "test-66-head.txt"
infile = "test-500-head.txt"
classes = list()

i = 1
z = 0
restp = {}
resfp = {}
## Populate list
while(i < argcount):
	classes.append(sys.argv[i])
	i = i + 1
print classes

## create dictionaries for results
while(z < len(classes)):
	restp[classes[z]] = 0
	resfp[classes[z]] = 0
	z = z + 1

thres = 0.56

reader = csv.reader( open(infile,'r'), delimiter = ' ')

for line in reader:
#	print line[2]
#	print ""
	if float(line[2]) < float(thres):
			print line
## Check sublabels by finding out difference between labels
			lineind = line[0].index('-') 
			print "lineind= ",lineind
			var = line[0][0:lineind]
			print "after strip= ",var.replace(".","")
			diff = math.fabs(int(line[0][0:lineind].replace(".","")) - int(line[1][0:lineind].replace(".","")))
#			print "diff= ",diff
			if (line[0][0:lineind] in classes):
				ind = classes.index(line[0][0:lineind])
				if  line[1][0:lineind] in classes and diff < 40:
					print "TP"
					print "Class = ",classes[ind]
					print line[0] +  " and " + line[1]
					restp[classes[ind]] = restp[classes[ind]] + 1
				if (line[0][0:lineind] != line[1][0:lineind]) and diff > 40:
#					ind = classes.index(line[0][0:lineind])
					print "FP"
					print "Class = ",classes[ind]
					print line[0] + " and " + line[1]
					resfp[classes[ind]] = resfp[classes[ind]] + 1
print "TP"
print restp
print "FP"
print resfp
#	if line
#print classes
