#######################################
# combined-ncdspam.py
# Functionality:
#
# 1. Use Cilibrasi and Vitanyi's Normalized Compression Distance
# to cluster a dataset of packet profiles.
# Author: Fahim Abbasi 20110316
# http://seat.massey.ac.nz/projects/honeynet
# Code based on wjt
# http://digitalhistoryhacks.blogspot.com
# 2. Calculate spamsum
# 3. Generate Graph
# 4. Generate UPGMA graph
# 5. Write combined spamsum + ncd score to file
#
# 20111205:
# Changed 'location' variable to be provided as command line parameter
# UPGMA file was redundant as the NCD output file is the same thing
# 20111220:
# Take 2 files as input and calculate NCD and spamsum scores and write
# the combined score to the result file
# 20120314:
# The combined score should be min(ncd,spsum)
# 20120318:
# Adding support to read model file and sig dir to create a list of signatures/exemplars
# 20120319:
# Move results to destination or output directory
# Removo list500.txt
# Usage:
# python get_scores.py --sigdir /home/fimz/Dev/datasets/balanced-raw/imbalanced-100 --datdir /home/fimz/Dev/datasets/testset --iter 1 --outdir /home/fimz/Dev/datasets/500-results/rev/profiles-raw --model mymodel.txt
######################################


#!/usr/bin/env python
import re, math, collections, sys , jellyfish
import os
import random
import zlib
import time
from decimal import *
import spamsum
import optparse

def tokenize( _str):
    stopwords = [',']
    tokens = collections.defaultdict(lambda: 0.)
    for m in re.finditer(r"(\w+)", _str, re.UNICODE):
#        m = m.group(1).lower()
 	m = m.group(1)
	if len(m) < 2: continue
        if m in stopwords: continue
        tokens[m] += 1

    return tokens
#end of tokenize


#pathstring = '/home/fimz/Dev/profiler/worm/exp-20110121-normal-n-worm/dataset/ncd'

## Function to calculate the Levenshtein, D-lev, Hamming, Jaro, Jaro-wink distance and KL and spamsum of the two files ##

def alldist(filex, filey):
    xread = open(filex, 'r').read()
    yread = open(filey, 'r').read()
## Take Reverse and append to original read ##
    rxread = xread + xread[::-1]
    ryread = yread + yread[::-1]
    xhash = spamsum.spamsum(rxread)
    yhash = spamsum.spamsum(ryread)
#    fx = open("/home/fimz/datasets/500-dataset/rev/test/"+filex+".rev", 'w')
#   fx.write(xhash)
#    fy = open("/home/fimz/datasets/500-dataset/rev/test/"+filey+".rev", 'w')
#    fy.write(yhash)
    spsum = spamsum.match(xhash,yhash)
    spsum = 100 - spsum
    spsum = float(spsum/100.00)

    return spsum

## Function to calculate the NCD of two files based on zlib level 9 compression ##

def ncd(filex, filey):
    xbytes = open(filex, 'r').read()
    ybytes = open(filey, 'r').read()
    xybytes = xbytes + ybytes
    cx = zlib.compress(xbytes,9)
    cy = zlib.compress(ybytes,9)
    cxy = zlib.compress(xybytes,9)
    if len(cy) > len(cx):
        n = (len(cxy) - len(cx)) / float(len(cy))
    else:
        n = (len(cxy) - len(cy)) / float(len(cx))
    return n

# Select all packet profiles from the path directory provided
# For each unique pair, calculate NCD
#
#
##############################################
##############################################
## Main program starts here ##
##############################################
##############################################

oparser = optparse.OptionParser(usage="usage: %prog [options] filename")
oparser.add_option("-s","--sigdir",
                   action="store",
                   dest = "sigdir",
                   default = False,
                   help = "path to signature directory")
oparser.add_option("-d","--datdir",
                   action="store",
                   dest = "datdir",
                   default = False,
                   help = "path to dataset directory")
oparser.add_option("-o","--outdir",
                   action="store",
                   dest = "outdir",
                   default = False,
                   help = "path to result output directory")
oparser.add_option("-i","--iter",
                   action="store",
                   dest = "itera",
                   default = False,
                   help = "iteration")
oparser.add_option("-g","--makegraph",
                   action='store_true',
                   dest = "make_graph",
                   default = False,
                   help = "Create graphs")
oparser.add_option("-n","--squarematrix",
                   action='store_true',
                   dest = "square_matrix",
                   default = False,
                   help = "Create graphs")
oparser.add_option("-m","--model",
                   action="store",
                   dest = "model",
                   default = False,
                   help = "Path to Model file")
oparser.add_option("-r","--random",
                   action="store",
                   dest = "rand",
                   default = False,
                   help = "Number of random exemplars to select")
oparser.add_option("-t","--threshold",
                   action="store",
                   dest = "thresh",
                   default = False,
                   help = "Threshold for fixed model")

(options, args) = oparser.parse_args()


location = options.outdir ## output or result dir
sigdir = options.sigdir  ## path to signature/exemplar dir
datdir = options.datdir  ## path to dataset dir
iteration = options.itera ## iterations
model = options.model  ## /path/to/model file
square_matrix = options.square_matrix
rand = int(options.rand) ## random picking

siglist = os.listdir(sigdir)
listing = os.listdir(datdir)
selection = []
sigselect = []
exemplars=[]
threshold = []

if(model):
    if(os.path.isfile("mymodel.txt")):
	f = open("mymodel.txt",'r') ## open model file to read
	lines = f.readlines() ## read file line by line
	for line in lines:
	   ex_label,ex_thresh = line.split(',') ## get exemplar and its threshold
	   exemplars.append(ex_label) ## append lables
	   threshold.append(ex_thresh) ## append threshold
	   if ex_label not in siglist:
		print "Copying exemplar:",ex_label
		os.system("cp "+datdir+"/"+ex_label+" "+sigdir)

## ADD SUPPORT FOR RANDOM EXEMPLAR PICKING ##

if(rand > 0):
	for i in range(0,rand):
		sigselect.append(random.choice(siglist))
	f = open("random_exemplars.txt",'w') ## open file to write
	for exemp in sigselect:
		f.write(exemp + "\n")
	f.close()

for infile in listing:
#    print "current file is: " + infile
    selection.append( infile )

## need to edit this to integrate with novelty
if square_matrix == 1:
	for infile in siglist:
		print "current file for sq_matrix is: " + infile
	        sigselect.append( infile )
else:
	for infile in siglist: ## for all the files in the signature list
	    if infile in exemplars:  ## if the file is an exemplar	
#		print "current file is: " + infile
		sigselect.append( infile ) ## append the file

print "sigselect: ",sigselect
print len(selection), selection[0]
now = "%s"%int(time.time())
ncdstr = "%s-ncd-out.txt"%now
#upgmastr = "%s-upgma-out.txt"%now
spsumstr = "%s-spsum-out.txt"%now
#combinedstr = "%s-combined-out.txt"%now
newcombinedstr = "%s-newcombined-out.txt"%now

output = "output/"

os.system("mkdir output")
#ncdfile = open( output+ncdstr, 'w')
#spsumfile = open( output+spsumstr,'w')
#combinedfile = open( output+combinedstr,'w')
newcombinedfile = open( output+newcombinedstr,'w')

## Reduntant upgma file, ncd is sufficient
#upgmafile = open (output+upgmastr, 'w')

getcontext().prec = 4

'''
for i in range(0, len(sigselect)):
#    print i
    for j in range(0, len(selection)):
        fx = sigdir + '/' + str(sigselect[i])
        fy = datdir + '/' + str(selection[j])
        print fx, fy
	ncdscore = ncd(fx,fy)
        ncdfile.write(str(sigselect[i]) + " " + str(selection[j]) + " " + str(+Decimal(str(ncdscore))) + "\n")
#        upgmafile.write("\'" + str(selection[i]) + "\'" + "," + "\'" + str(selection[j]) + "\'" + "," + str(ncd(fx, fy))+ "\n")
## Reduntant upgma file, ncd is sufficient
        upgmafile.write(str(sigselect[i]) + "," + str(selection[j]) + "," +  str(+Decimal(str(ncdscore))) + "\n" )
## Get Scores ##
	spsum = alldist(fx, fy)
	combscore = float(spsum) + float(ncdscore)
#	print "scores: ",lev, dlev, jaro, jarowink, ham, kl, spsum
#	print "type: ", type(spsum)
## Write them out ##
       	spsumfile.write(str(sigselect[i]) + " " + str(selection[j]) + " " + str(spsum) + "\n")
#	newcombinedfile.write(str(selection[j]) + " " + str(sigselect[i]) + " " + str(combscore) + "\n")
	combinedfile.write(str(sigselect[i]) + " " + str(selection[j]) + " " + str(combscore) + "\n")
'''

for i in range(0, len(selection)):
#    print i
    for j in range(0, len(sigselect)):
        fx = sigdir + '/' + str(sigselect[j])
        fy = datdir + '/' + str(selection[i])
	ncdscore = ncd(fx,fy)		 
	spsum = alldist(fx, fy)
	combscore = []
        combscore = [float(spsum) , float(ncdscore)]
        newcombinedfile.write(str(selection[i]) + " " + str(sigselect[j]) + " " + str(min(combscore)) + "\n")
#        ncdfile.write(str(selection[i]) + " " + str(sigselect[j]) + " " + str(ncdscore) + "\n")
#        spsumfile.write(str(selection[i]) + " " + str(sigselect[j]) + " " + str(spsum) + "\n")
#        upgmafile.write(str(selection[i]) + " " + str(sigselect[j]) + " " + str(ncdscore) + "\n")
#        combinedfile.write(str(selection[i]) + " " + str(sigselect[j]) + " " + str(ncdscore) + " " + str(spsum)  + "\n")



#ncdfile.close()
#upgmafile.close()
#spsumfile.close()
#combinedfile.close()
newcombinedfile.close()

print "Distances Successfully calculated and written out to files"

if options.make_graph == 1:
	print "##########################################################"
	print "Calculating graph"
#	os.system("python ncd-fimz-graph.py " +ncdstr  + " " + "0.65" )
#	os.system("python ncd-fimz-graph.py " +spsumstr+ " " + "0.95"  )
	os.system("python ncd-fimz-graph.py " +newcombinedstr + " " + "1.55" )


#	graphncd = "output/graph-" + ncdstr
#	graphspsum = "output/graph-" + spsumstr
	graphcombined = "output/graph-" + newcombinedstr

#	ncdpng = graphncd + ".svg"
#	spsumpng = graphspsum + ".svg"
	newcombinedpng = graphcombined + ".svg"


	print "Graph files Created"
	print "##########################################################"
	print "Running Neato on ncd"

#	os.system("sfdp -Tsvg "+ graphncd + " -o " + ncdpng)
	#os.system("sfdp -Tpng "+ graphncd + " -o " + ".png")

	print "Running Neato on spsum"
#	os.system("sfdp -Tsvg "+ graphspsum + " -o " + spsumpng)

	print "Running Neato on combined"
#	os.system("sfdp -Tsvg "+ graphcombined + " -o " + combinedpng)

	## Adding UPGMA support
	print "Calculating UPGMA"
#	os.system("python upgma.py output/" + upgmastr)
	os.system("python upgma.py output/" + newcombinedstr)

## Removing list500.txt ##
#os.system("rm -f list500.txt")
## Append to output to create the list ##

f = open("list500.txt",'w')

#location = "/home/fimz/Dev/datasets/500-results"
print "location: ",location
print "ncdstr: ",ncdstr
#finalncd = location + "/" +  ncdstr
#finalspsum = location + "/" + spsumstr
#finalcombined = location + "/" + combinedstr
finalnewcombined = location + "/" + newcombinedstr
print "Final result file:",finalnewcombined
#f.write(finalncd  + "\n")
#f.write(finalspsum  + "\n")
#f.write(finalcombined  + "\n")
f.write(finalnewcombined  + "\n")

f.close()
f = open("result.file",'w')
f.write(finalnewcombined)
f.close()
os.system("mv output/* "+location+"/") ## MOVE TO OUTPUT DIR


