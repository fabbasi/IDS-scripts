import numpy as np
from sklearn.cluster import AffinityPropagation
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
import dynamic,csv,os,sys,math

def matrix_from_pairs(pairs):
    """Takes a list of pairs and their distances and creates the distance matrix.

    The list elements should have the format:

        (name1, name2, value)

    It will return a matrix with all the values, plus the list of labels.
    """

    labels = set()
    labels.update([x[0] for x in pairs]+[x[1] for x in pairs])
    labels = list(labels)
    labels.sort()

    dimension = len(labels)
    distance_matrix = np.zeros( (dimension, dimension), 'f')

    for pair in pairs:
        i = labels.index(pair[0])
        j = labels.index(pair[1])
        distance_matrix[i][j] = -1*float(pair[2]) ## negating for affinity

    return distance_matrix, labels

fname = sys.argv[1]
pairs = []
categories, topLevelCategories = dynamic.loadCategories("categories-500.txt") ## Load categories from cat file
resfile = csv.reader(open(fname, 'r'), delimiter=" ")
for row in resfile:
        pairs.append(row)

distance_matrix, orig_labels = matrix_from_pairs(pairs)
hlabels = orig_labels[:]
hlabels.insert(0,0)
writer = csv.writer(open("matrix.csv",'w'),delimiter = ',')
writer.writerow(hlabels)
temp = []
counter = 0
for row in distance_matrix:
   if counter <= max:
        temp = list(row)
        temp.insert(0,orig_labels[counter])
	writer.writerow(temp)
        counter = counter + 1

print distance_matrix

##############################################################################
# Generate sample data
centers = [[1, 1], [-1, -1], [1, -1]]
X, labels_true = make_blobs(n_samples=300, centers=centers, cluster_std=0.5)
print "X b4:",X
print "labels true:", labels_true
##############################################################################
# Compute similarities
X_norms = np.sum(X ** 2, axis=1)
T_norms = np.sum(distance_matrix ** 2,axis =1)
#print "T norm:", T_norms
S = - X_norms[:, np.newaxis] - X_norms[np.newaxis, :] + 2 * np.dot(X, X.T)
T_S = - T_norms[:, np.newaxis] - T_norms[np.newaxis, :] + 2 * np.dot(distance_matrix, distance_matrix.T)

#print "T_S:",S
p = 2 * np.median(distance_matrix)
pref = -3
#print "S:",S
print "P:",p
c_results = [] ## to hold the number of clusters
p_results = [] ## hold the pref value
##############################################################################
# Compute Affinity Propagation

#while( pref > -200):
af = AffinityPropagation().fit(distance_matrix, pref)
cluster_centers_indices = af.cluster_centers_indices_
labels = af.labels_
print "Labels:",labels
print "indices",cluster_centers_indices
n_clusters_ = len(cluster_centers_indices)
print "preference: ", pref
print 'Estimated number of clusters: %d' % n_clusters_
c_results.append(float(n_clusters_))
p_results.append(float(pref))
#print "Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels)
#print "Completeness: %0.3f" % metrics.completeness_score(labels_true, labels)
#print "V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels)
#print "Adjusted Rand Index: %0.3f" % \
#    metrics.adjusted_rand_score(labels_true, labels)
#print "Adjusted Mutual Information: %0.3f" % \
#    metrics.adjusted_mutual_info_score(labels_true, labels)
D = (S / np.min(S))
print ("Silhouette Coefficient: %0.3f" %
       metrics.silhouette_score(D, labels, metric='precomputed'))
#	pref = pref - 1

#minclust = min(c_results)
#print "Optimal cluster result: ",minclust
#print "Corresponding pref: ",p_results[c_results.index(min(c_results))]

##############################################################################
# Plot result
import pylab as pl
from itertools import cycle

pl.close('all')
pl.figure(1)
pl.clf()

colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
for k, col in zip(range(n_clusters_), colors):
    class_members = labels == k
    cluster_center = distance_matrix[cluster_centers_indices[k]]
    print "k:",k
#    print "center:",cluster_center
    pl.plot(distance_matrix[class_members, 0], distance_matrix[class_members, 1], col + '.')
    pl.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
            markeredgecolor='k', markersize=14)
    for x in distance_matrix[class_members]:
        pl.plot([cluster_center[0], x[0]], [cluster_center[1], x[1]], col)
#	print x

pl.title('Estimated number of clusters: %d' % n_clusters_)
#pl.show()
pl.savefig('affinity.png')

