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
os.system("touch knn.txt")
os.system("touch knn-select.txt")

################################
# slide the number of exemplars
################################

x_list = []
y_list = []
k = 3
os.system("python get_scores.py -s /home/fimz/Dev/datasets/balanced-raw/10-each -d /home/fimz/Dev/datasets/balanced-raw/10-each -n -o /home/fimz/Dev/datasets/500-results/random")
os.system("python e-nn.py " + str(k)+ " " + "/home/fimz/Dev/datasets/balanced-raw/10-each" + " " + "/home/fimz/Dev/datasets/500-results/random/")
os.system("mv output/* "+resultf) ## move results to result dir
os.system("mv knn* /home/fimz/Dev/datasets/500-results/random/")

#   os.system("mv *-500-dyn-result* "+resultf) ## move results to result dir
#   os.system("mv roc-results* /home/fimz/Dev/datasets/500-results/random/")
#   os.system("mv final-roc* /home/fimz/Dev/datasets/500-results/random/")

