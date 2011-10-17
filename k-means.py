import scipy
from numpy import *
from scipy.cluster.vq import *
#class1 = array(random.standard_normal((100,2))) + array([5,5])
#class2 = 1.5 * array(random.standard_normal((100,2)))
a = open("A.txt",'r').readlines()
f = open("A.txt",'r').readlines()
labela = []
labelf = []
thres = 0.55
thres = float(thres)
for val in a:
	val = val.strip('\n')
	val = val.strip()
#	if val != "":
#		print "In Val: ",val
#		b = float(val)
#		print "In b:",b
#		if float(b) <= thres:
#			print "In Condition: %s"%b
	labela.append(val)	

for val in f:
#	if val != "" and float(val) < 0.55:
	val = val.strip('\n')
	val = val.strip()
#	if val != "":
#		b = float(val)
#		if b < 0.55:
	labelf.append(val)

tmpa = [[float(p)] for p in labela if p != ""]
tmpf = [[float(p)] for p in labelf if p != ""]

class1 = scipy.array(tmpa)
class2 = scipy.array(tmpf)

features = vstack((class1,class2))
centroids,variance = kmeans(features,2)
code,distance = vq(features,centroids)
import pylab
pylab.plot([p[0] for p in class1],'*')
pylab.plot([p[0] for p in class2],'r*')
pylab.plot([p[0] for p in centroids],'go')
pylab.show()
