import numpy
from numpy import random,argsort,sqrt,nonzero
from pylab import plot,show
import csv,os,sys,numpy,dynamic,math
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.mlab as mlab


fname = open("result.file",'r').read()
pairs = []
categories, topLevelCategories = dynamic.loadCategories("categories-500.txt") ## Load categories from cat file
resfile = csv.reader(open(fname, 'r'), delimiter=" ")
for row in resfile:
        pairs.append(row)

labels = set()
exemplars = set()
for x in pairs:
#   print x
   labels.update([x[0]])
   exemplars.update([x[1]])

labels = list(labels)
exemplars = list(exemplars)
labels.sort()
exemplars.sort()
dimension_r = len(labels)
dimension_c = len(exemplars)
distance_matrix = numpy.zeros( (dimension_r, dimension_c), 'f')
for pair in pairs:
#    print pair
    i = labels.index(pair[0])
    j = exemplars.index(pair[1])
#    print "i: ",i
#    print "j: ",j
    distance_matrix[i][j] = float(pair[2])

vlabels = labels[:]
hlabels = exemplars[:]
hlabels.insert(0,0)
vlabels.insert(0,0)
writer = csv.writer(open("matrix.csv",'w'),delimiter = ',')
writer.writerow(hlabels)
temp = []
counter = 0
for row in distance_matrix:
   if counter <= max:
        temp = list(row)
        temp.insert(0,labels[counter])
        writer.writerow(temp)
        counter = counter + 1

counter = 0
tp = fp = 0
for row in distance_matrix:
	idx = nonzero(row==min(row))[0][0]
#	print("datapoint = %s, index = %s , exemplar/neighbor = %s") % (labels[counter] , idx , exemplars[idx])
        part1Class, part1Details = labels[counter].split("-")
        category1 = dynamic.categorisePayload(part1Class, categories)           # Classify the header -> return 14 for 14.1, 14.1.1, 14.1.2
        part2Class, part2Details = exemplars[idx].split("-")
        category2 = dynamic.categorisePayload(part2Class, categories)           # Classify the header -> return 14 for 14.1, 14.1.1, 14.1.2
	if category1 == category2:
		print("datapoint = %s, index = %s , exemplar/neighbor = %s , TP") % (labels[counter] , idx , exemplars[idx])
		tp = tp + 1
	if category1 != category2:
		print("datapoint = %s, index = %s , exemplar/neighbor = %s , FP") % (labels[counter] , idx , exemplars[idx])
		fp = fp + 1
	counter = counter + 1

print "Exemplars: ", dimension_c
print "Datapoints: ", dimension_r
print "Total TP = ",tp
print "Total FP = ",fp

f = open("nn.txt",'a')
f.write("\n####### NEW RECORD ########")
f.write( "\nExemplars: " + str(dimension_c) )
f.write( "\nDatapoints: " + str(dimension_r) )
f.write( "\nTotal TP = " + str(tp) )
f.write( "\nTotal FP = " + str(fp) )
f.close()
