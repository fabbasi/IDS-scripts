import numpy
from numpy import random,argsort,sqrt,nonzero
from pylab import plot,show
import csv,os,sys,numpy,dynamic,math
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.mlab as mlab

def get_matrix(pairs):
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
	return distance_matrix,labels,exemplars

def k_nearest_neighbor(distance_matrix,labels,exemplars,k,sourcedir,destdir):
	counter = 0
	tp = fp = 0
	knn_index = []
	selection = set()
	for row in distance_matrix:
		idx = argsort(row)
#		print "idx = ",idx
#		print "k = ",k
		knn_index = idx[:int(k)]
		w_cat = 0 ## wrong category
		r_cat = 0 ## right category
		tp_once = 0
		for x in knn_index:
		#	print("datapoint = %s, index = %s , exemplar/neighbor = %s") % (labels[counter] , idx , exemplars[idx])
			part1Class, part1Details = labels[counter].split("-")
			category1 = dynamic.categorisePayload(part1Class, categories)           # Classify the header -> return 14 for 14.1, 14.1.1, 14.1.2
			part2Class, part2Details = exemplars[x].split("-")
			category2 = dynamic.categorisePayload(part2Class, categories)           # Classify the header -> return 14 for 14.1, 14.1.1, 14.1.2
			if category1 != category2:
				w_cat = w_cat + 1
				print("datapoint = %s, index = %s , exemplar/neighbor = %s , FP") % (labels[counter] , idx[:int(k)] , exemplars[x])

			else:
				r_cat = r_cat + 1
				print("datapoint = %s, index = %s , exemplar/neighbor = %s , TP") % (labels[counter] , idx[:int(k)] , exemplars[x])

		if r_cat > w_cat:
			tp = tp + 1
			print "Majority vote True: ", r_cat
			print "Adding to set: ", labels[counter]
			selection.add(labels[counter])
		else:
			fp = fp + 1
			print "Majority vote False: ", w_cat
		counter = counter + 1

	dimension_c = len(exemplars)
	dimension_r = len(labels)
	print "Exemplars: ", dimension_c
	print "Datapoints: ", dimension_r
	print "Total TP = ",tp
	print "Total FP = ",fp
	selection = list(selection)
	selection.sort()
	s = open("knn-select.txt",'a')
	for item in selection:
		s.write("\n" + str(item))
		os.system("cp " + sourcedir + "/" + str(item) + " " + destdir)
	s.close()
	print "Selection set size: ", len(selection)
	f = open("knn.txt",'a')
#	f.write("\n####### NEW RECORD ########")
#	f.write( "\nExemplars: " + str(dimension_c) )
#	f.write( "\nDatapoints: " + str(dimension_r) )
	f.write( "\n" + k + ","  + str(dimension_c) + "," + str(dimension_r) + "," + str(tp) + "," + str(fp) )
#	f.write( "\nTotal FP = " + str(fp) )
	f.close()

#### MAIN STARTS HERE ####

k = sys.argv[1]
sourcedir = sys.argv[2]
destdir = sys.argv[3]
print "k = ",k
fname = open("result.file",'r').read()
pairs = []
categories, topLevelCategories = dynamic.loadCategories("categories-500.txt") ## Load categories from cat file
resfile = csv.reader(open(fname, 'r'), delimiter=" ")
for row in resfile:
        pairs.append(row)

distance_matrix,labels,exemplars = get_matrix(pairs)

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

k_nearest_neighbor(distance_matrix,labels,exemplars,k, sourcedir, destdir)


