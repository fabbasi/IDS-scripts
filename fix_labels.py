###########################
# fix_labels.py
# Description: This script will read any given dataset path supplied as a command line argument and search for samples without labels.
# All these unlabelled samples will then be used by the get_score.py script to calculate the score and then maybe the get_roc.py script for roc.
# Author: Fahim Abbasi
# Email: f.abbasi@massey.ac.nz
##########################
#!/usr/bin/env python
import os,sys

targetdir = sys.argv[1] ## path to target dataset folder

targetlist = os.listdir(targetdir)
correctedlist = []

for item in targetlist:
	if "-" not in item:
		fixeditem = "X-" + item
		os.system("mv "+targetdir+"/"+item+" "+targetdir+"/"+fixeditem)
		correctedlist.append(fixeditem)

print "Listing items: ",correctedlist
print "Fixed samples: ",len(correctedlist)

