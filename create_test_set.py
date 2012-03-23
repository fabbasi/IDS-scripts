#!/usr/bin/env python

######################################################################
## CREATE A TEST SET FROM A GIVEN TRAINING SET AND THE MAIN DATASET ##
######################################################################

import os,sys,dynamic,optparse

testset = []
oparser = optparse.OptionParser(usage="usage: %prog [options] filename")
oparser.add_option("-t","--traindir",
                   action="store",
                   dest = "traindir",
                   default = False,
                   help = "path to training directory")
oparser.add_option("-d","--datasetdir",
                   action="store",
                   dest = "datdir",
                   default = False,
                   help = "path to dataset directory")

(options, args) = oparser.parse_args()

traindir = options.traindir
datdir = options.datdir

trainlist = os.listdir(traindir)
datlist = os.listdir(datdir)


for infile in datlist:
   if infile not in trainlist:	
	testset.append(infile)

print testset
print "len",len(testset)

os.system("mkdir testset")

for tfile in testset:
	os.system("cp "+datdir+tfile+" testset/")
