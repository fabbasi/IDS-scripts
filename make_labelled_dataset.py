#!/usr/bin/env python

###################################
# Author: Fahim Abbasi
# Date: 20110510
# Description: The make_profiles scripts job is to prepare a dataset of labelled data from tillmanns dataset. The labels are assigned to the name of the file while the raw data is written into it.
###################################

import sys
import os
import time
import errno
import hashlib
import csv

print "1 arguments required <target directory/>"

datasetdir = sys.argv[1]

#reportdir = "./report"

try:
	os.makedirs("./profiles-raw")
except os.error, e:
	if e.errno != errno.EEXIST:
		raise

listing = os.listdir(datasetdir)
selection = [] 
count = 1
print "List length= ", len(listing)
for infile in listing:
		print "Current file is: " + datasetdir + infile
		myfile =  datasetdir + infile
		f = open(myfile,'r').read()
		mhash = hashlib.md5(f).hexdigest()
		print "Iteration: ", count
		print "md5 Hash is: " + mhash
		reader = csv.reader(open("/home/fimz/Dev/datasets/tillmann/dataset/labels.txt", "r"), delimiter='\t')
		for rows in reader:
		     if mhash in rows:
			     print rows
			     print "Label = ", rows[1]
		             label = rows[1]

		logfile = label + "-" + mhash + ".raw"
		fp = open("./profiles-raw/" + logfile, 'w')
		fp.write( f )
		print "Written to file successfully"
#		os.system("python get_streams.py "+ pathstr + "/" + infile )		
		count = count + 1

