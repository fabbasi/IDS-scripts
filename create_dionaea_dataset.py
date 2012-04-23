##################################
# create_dionaea_dataset.py
#
# Description:
# Creates a dataset from dionaea bistreams.
# Copies streams and writes them out to the destination renaming them to their md5sum.
# Creates a list of the mapping between the md5sum and the original filename
#
#
#
#
#
################################


#!/usr/bin/python

import sys, os, hashlib, errno, re

print "2 arguments required <source dionaea dataset dir> <target dataset directory/>"

source = sys.argv[1]
dest = sys.argv[2]

listing = os.listdir(source)

try:
	        os.makedirs(dest)
except os.error, e:
	        if e.errno != errno.EEXIST:
			        raise

mapf = open("/home/fimz/Dev/datasets/dionaea-mapping.txt",'w')
for folder in listing:
   loc = source+"/"+folder	
   listofsamples = os.listdir(loc)
   for sample in listofsamples:
	print "Current file is: " + source + "/" + sample
	myfile = loc + "/" + sample
	inf = open(myfile,'r').read()  ## read the source file
	mhash = hashlib.md5(inf).hexdigest()  ## create an md5sum of the source
	outf = open(dest+"/"+"X-"+mhash,'w') ## open output file for writting
	temp = inf.strip("stream = [('in', b' ")
	temp = temp.strip("')]")
	final = temp.replace("('in', b'",'')
	final = final.replace("('out', b'",'')
#	final = re.sub(r'.*(\'\),\(\'out\', b\').*','\n', temp)
#	final = re.sub(r'.*(\(\'out\', b\').*','\n', final)
#	final = re.sub(r'.*(\(\'in\', b\').*','\n ', final)


	outf.write(final)	## Write to the newly renamed file
	mapf.write(sample + " " + mhash + "\n") ## append to the mapping file
#	inf.close()
	outf.close()

mapf.close()





