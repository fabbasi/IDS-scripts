###########################
# Step through various threshold values and create a confusion matrix.
# Generate an ROC curve from this confusion matrix
#
#
##########################

import sys, os, pylab, numpy, scipy

#============================================
# DRAW ROC CURVE roc(xlist,ylist,filename)
#===========================================
def roc(xlist,ylist,filename,title,xlabel,ylabel):
        global user_threshold
        pylab.title(title)
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        pylab.plot(xlist, ylist, 'r')
        pylab.xticks(scipy.arange(0,1.01,0.1))
        pylab.yticks(scipy.arange(0,1.01,0.1))
        pylab.ylim(ymin = 0, ymax = 1.01)
        pylab.xlim(xmin=-.025, xmax = 1.01)
        #fig.show()
        ## Save plot as PNG
        pylab.grid(True)
        pylab.savefig(filename + '.png')
        pylab.close()



i=0
resultf = "/home/fimz/Dev/datasets/500-results/random/"
os.system("touch roc-results.txt")
os.system("touch knn.txt")

################################
# slide the number of exemplars
################################

for exemp_num in range(1,10):
   for iterate in range(10):	
	x_list = []
	y_list = []
	os.system("python get_scores.py -s /home/fimz/Dev/datasets/balanced-raw/10-each -d /home/fimz/Dev/datasets/good-testset -o /home/fimz/Dev/datasets/500-results/random -r %s" % exemp_num)
	print exemp_num
#	for k in range(1,6,2):
#		os.system("python k-nearest_neighbor.py " + str(k))
	while i < 1:
		i = i + 0.05
		print i
		os.system("python get_roc_for_random.py %s 3 /home/fimz/Dev/datasets/500-results/random/ %s" % (i,str(exemp_num)) )
	i = 0
#   f = open("roc-results.txt","r").readlines()
#   for item in f:
#	print item
#	item = item.strip()
#	thresh,dcount,scount,tp,fp,fn,tn,y,x,unknown,acc,auc,p,test = item.split(",")
#	x_list.append(str(x))
#	y_list.append(str(y))
## Copy the results to the appropriate result exemplar file ##
   os.system( "cp roc-results.txt " + "roc-results-"+ str(exemp_num) + ".txt" )
   xlabel = "FPR"
   ylabel = "TPR"
   title = "ROC"
   fname = "final-roc-"+str(exemp_num)
   print "xlist:",x_list
   print "ylist:",y_list
   x_list, y_list = zip(*sorted(zip(x_list, y_list)))  ## sort axis coordinates for ROC
   roc(x_list,y_list,fname,title,xlabel,ylabel)
   print "ROC created"
   os.system("mv output/* "+resultf) ## move results to result dir
#os.system("mv knn* /home/fimz/Dev/datasets/500-results/random/")

   os.system("mv *-500-dyn-result* "+resultf) ## move results to result dir
   os.system("mv roc-results* /home/fimz/Dev/datasets/500-results/random/")
   os.system("mv final-roc* /home/fimz/Dev/datasets/500-results/random/")

