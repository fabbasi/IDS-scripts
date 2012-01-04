#!/usr/bin/env python

###################################
# Author: Fahim Abbasi
# Date: 20110510
# Description: The make_profiles scripts job is to prepare a dataset of labelled data from tillmanns dataset. The labels are assigned to the name of the file and the fuzzy hash of the file is written into it.
###################################

import sys
import os
import time
import re
import spamsum
import errno
import hashlib
import csv

print "2 arguments required <file list> <target directory/>"

#filelist = sys.argv[1]
datasetdir = sys.argv[1]

#reportdir = "./report"
"""
flist = list()
f = open(filelist,"r")
for line in f.xreadlines():
        line = line.strip('\n')
        flist.append(line)
        print line
f.close()
"""
#inc = 0
#while "0" in pathstr:
try:
	os.makedirs("./profiles")
except os.error, e:
	if e.errno != errno.EEXIST:
		raise

listing = os.listdir(datasetdir)
selection = [] 
count = 1
print "List length= ", len(listing)
for infile in listing:
		print "Current file is: " + datasetdir + infile
#		print "File Submitted Successfully"
	#temphash = infile.split(".")	
		myfile =  datasetdir + infile
	#	fhash = temphash[0]
		f = open(myfile,'r').read()
#		res = re.findall(r'"scan_id": "(\w.*)",',f)
#		if res:
		mhash = hashlib.md5(f).hexdigest()
		fhash = spamsum.spamsum(f)
		#f.close()
		print "Iteration: ", count
		print "md5 Hash is: " + mhash
		print "Fuzzy Hash is: " + fhash
		reader = csv.reader(open("/home/fimz/Dev/tillmann/dataset/labels.txt", "r"), delimiter='\t')
		for rows in reader:
		     if mhash in rows:
			     print rows
			     print "Label = ", rows[1]
		             label = rows[1]
  			     logfile = label + "-" + mhash + ".fuzz"
   			     fp = open("./profiles/" + logfile, 'w')
    			     fp.write( fhash )
   			     print "Written to file successfully"
			     count = count + 1

