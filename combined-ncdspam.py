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
# 
######################################


#!/usr/bin/env python
import re, math, collections, sys , jellyfish
import os
import random
import zlib
import time
from decimal import *
import spamsum

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
    xhash = spamsum.spamsum(xread)
    yhash = spamsum.spamsum(yread)
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
    cxy = zlib.compress(xybytes)
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

location = sys.argv[3]
pathstring = sys.argv[1]
iteration = sys.argv[2]

listing = os.listdir(pathstring)
selection = []
for infile in listing:
    print "current file is: " + infile
    selection.append( infile )

print len(selection), selection[0]
now = "%s"%int(time.time())
ncdstr = "%s-ncd-out.txt"%now
upgmastr = "%s-upgma-out.txt"%now
spsumstr = "%s-spsum-out.txt"%now
combinedstr = "%s-combined-out.txt"%now

output = "output/"

os.system("mkdir output")
ncdfile = open( output+ncdstr, 'w')
spsumfile = open( output+spsumstr,'w')
combinedfile = open( output+combinedstr,'w')

## Reduntant upgma file, ncd is sufficient
upgmafile = open (output+upgmastr, 'w')

getcontext().prec = 4

for i in range(0, len(selection)):
#    print i
    for j in range(0, len(selection)):
        fx = pathstring + '/' + str(selection[i])
        fy = pathstring + '/' + str(selection[j])
        print fx, fy
	ncdscore = ncd(fx,fy)
        ncdfile.write(str(selection[i]) + " " + str(selection[j]) + " " + str(+Decimal(str(ncdscore))) + "\n")
#        upgmafile.write("\'" + str(selection[i]) + "\'" + "," + "\'" + str(selection[j]) + "\'" + "," + str(ncd(fx, fy))+ "\n")
## Reduntant upgma file, ncd is sufficient
        upgmafile.write(str(selection[i]) + "," + str(selection[j]) + "," +  str(+Decimal(str(ncdscore))) + "\n" )
## Get Scores ##
	spsum = alldist(fx, fy)
	combscore = float(spsum) + float(ncdscore)
#	print "scores: ",lev, dlev, jaro, jarowink, ham, kl, spsum
#	print "type: ", type(spsum)
## Write them out ##
       	spsumfile.write(str(selection[i]) + " " + str(selection[j]) + " " + str(spsum) + "\n")
       	combinedfile.write(str(selection[i]) + " " + str(selection[j]) + " " + str(combscore) + "\n")

ncdfile.close()
upgmafile.close()
spsumfile.close()
combinedfile.close()
print "Distances Successfully calculated and written out to files"
print "##########################################################"
print "Calculating graph"
os.system("python ncd-fimz-graph.py " +ncdstr + " " + "0.65")
os.system("python ncd-fimz-graph.py " +spsumstr + " " + "0.95")
os.system("python ncd-fimz-graph.py " +combinedstr + " " + "1.55")


graphncd = "output/graph-" + ncdstr
graphspsum = "output/graph-" + spsumstr
graphcombined = "output/graph-" + combinedstr

ncdpng = graphncd + ".svg"
spsumpng = graphspsum + ".svg"
combinedpng = graphcombined + ".svg"


print "Graph files Created"
print "##########################################################"
print "Running Neato on ncd"

os.system("sfdp -Tsvg "+ graphncd + " -o " + ncdpng)
#os.system("sfdp -Tpng "+ graphncd + " -o " + ".png")

print "Running Neato on spsum"

os.system("sfdp -Tsvg "+ graphspsum + " -o " + spsumpng)

print "Running Neato on combined"

os.system("sfdp -Tsvg "+ graphcombined + " -o " + combinedpng)


## Adding UPGMA support
print "Calculating UPGMA"

os.system("python upgma.py output/" + upgmastr)

## Removing list500.txt ##
#os.system("rm -f list500.txt")
## Append to output to create the list ##

f = open("list500.txt",'a')

#location = "/home/fimz/Dev/datasets/500-results"
finalncd = location + "/" + iteration + "/" + ncdstr
finalspsum = location + "/" + iteration + "/" + spsumstr
finalcombined = location + "/" + iteration + "/" + combinedstr

f.write(finalncd  + "\n")
f.write(finalspsum  + "\n")
f.write(finalcombined  + "\n")

f.close()

