## upgma.py
## Usage: upgma.py <file containing ncd pairs>
## Important functions:
## graph = graph_from_upgma(upgma(*matrix_from_pairs(pairs)))
## graph.write_png('example1_graph.png')

import sys
import os
import re
import pydot
import csv
import time

try:
	set
except NameError:
	from sets import Set as set


#from sets import Set
#from Numeric import array, transpose, zeros
from numpy import array, transpose, zeros

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
    distance_matrix = zeros( (dimension, dimension), 'f')

    for pair in pairs:
        i = labels.index(pair[0])
        j = labels.index(pair[1])
        distance_matrix[i][j] = float(pair[2])
        distance_matrix[j][i] = float(pair[2])
            
    return map(list, distance_matrix), labels



def _upgma(labels):
    global new_matrix

    if len(labels) == 2:
        return (labels[0], labels[1])
    
    min_dist = None
    closest = None
    matrix = new_matrix
    print len(matrix[0])
    for i in range(len(matrix[0])-1):
        row = matrix[i][i+1:]
        min_row_dist = min(row)
        if not min_dist or min_row_dist<min_dist:
            min_dist = min_row_dist
            closest = (i, row.index(min_dist) + i + 1)
			
    cluster_row = []
    del new_matrix
    new_matrix = []
    for i in range(len(matrix[0])):
        if i in closest:
            continue
        cluster_row.append((matrix[closest[0]][i] + matrix[closest[1]][i])/2.0)
        new_matrix.append([matrix[i][j] for j in range(len(matrix[0])) if j not in closest])
    del matrix
    
    
    new_matrix = array( [cluster_row]+new_matrix )
    new_matrix = transpose(new_matrix).tolist()
    new_matrix = array( [[0,]+cluster_row]+new_matrix )
    new_matrix = transpose(new_matrix).tolist()
    
    new_labels = [(labels[closest[0]], labels[closest[1]], min_dist)]+	\
        [labels[i] for i in range(len(labels)) if i not in closest]

    del cluster_row, row, closest, labels
    return _upgma(new_labels)
	

def upgma(matrix, labels):
    global new_matrix
    
    new_matrix = matrix
    return _upgma(labels)


def plot_dendrogram(dendrogram, parent, graph):
    global cluster_cnt

    if len(dendrogram)>1:
        for node in dendrogram:
            if isinstance(node, tuple) and len(node)>1:
                label = 'cluster_%d' % cluster_cnt
                cluster_cnt += 1
                                
                graph.add_node(pydot.Node(
                    label,
#		     label = cluster_cnt,	
                    label= str(cluster_cnt) + " " + str('D=%3.2f%%\\nS=%3.2f%%' % (
                       100*node[-1], 100*(1-node[-1]))),
#                    shape='circle',
                    color='lightskyblue3'))

                # they are closely related, make a cluster
		# Threshold value 0.65
                if node[-1]<0.65:
                    cluster = pydot.Cluster(label)
                    cluster.set_bgcolor('beige')
                    graph.add_subgraph(cluster)
                    plot_dendrogram(node[:-1], label, cluster)
		else:
                    plot_dendrogram(node[:-1], label, graph)                
              
            else:
                label = str(node)
                
            graph.add_edge(pydot.Edge(parent, label))
     
#    graph.write_png('example2_graph.png')

def graph_from_upgma(dendrogram):
    global cluster_cnt
    
    cluster_cnt = 0

    graph = pydot.Dot(graph_type='graph')
    graph.add_node(pydot.Node(
#        'node', style='filled', shape='box', color='lightskyblue3'))
        'node', style='filled', color='lightblue2'))

    graph.add_node(pydot.Node('edge', color='lightgray'))
#    graph.add_node(pydot.Node('edge', color='lightblue2'))

    graph.set_rankdir('LR')
        
    parent = 'root'
    
    plot_dendrogram(dendrogram, 'root', graph)	
                
    return graph
"""
val =  [
	['A','A',0],
	['A','B',0.5],
	['A','C',0.7],
	['A','D',0.6],
	['A','E',0.8],
	['B','A',0.6],
	['B','B',0],
	['B','C',0.4],
	['B','D',0.5],
	['B','E',0.7],
	['C','A',0.4],
	['C','B',0.6],
	['C','C',0],
	['C','D',0.7],
	['C','E',0.8],
       ]

test = 	[
	 ['301-192.168.10.126-6.445','301-192.168.10.126-6.445',0.0387596899225],
	 ['301-192.168.10.126-6.445','908-192.168.10.125-17.53',0.702290076336],
	 ['301-192.168.10.126-6.445','701-192.168.10.102-17.53',0.77519379845],
	 ['301-192.168.10.126-6.445','5-24.6.98.163-6.80',0.77519379845],
	 ['301-192.168.10.126-6.445','706-80.68.89.43-6.34800',0.782945736434],
	 ['301-192.168.10.126-6.445','113-24.6.102.196-6.1588',0.84496124031],
	 ['301-192.168.10.126-6.445','100-218.232.95.60-17.1434',0.751937984496],
	 ['301-192.168.10.126-6.445','602-192.168.10.126-6.110',0.713178294574],
	 ['301-192.168.10.126-6.445','901-192.168.10.125-6.80',0.728571428571],
	]

test2 = [
	 ['A','A',0.0387596899225],
	 ['A','B',0.702290076336],
	 ['A','C',0.77519379845],
	 ['B','A',0.77519379845],
	 ['B','B',0.082945736434],
	 ['B','C',0.84496124031],
	 ['C','A',0.751937984496],
	 ['C','B',0.713178294574],
	 ['C','C',0.0728571428571],
	]
"""

#print "Val=",val
#print type(val)
#valfile = open( "val.out",'w')
#valfile.write(str(val))

#print "Test=",test
fname = sys.argv[1]
#print "Test2=",test2
pairs = []
ncdfile = csv.reader(open(fname, 'r'), delimiter=",")
#pairs = ncdfile.readlines()
for rows in ncdfile:
#	print rows
	pairs.append(rows)


#ncdfile.close()
#print type(pairs )
#pairs = val
#print "Pairs",pairs
#view = matrix_from_pairs(val)

#view = matrix_from_pairs(pairs)
#print "Data=",view[0]
#mat = test[0]
#print "Label=",view[1]
#lab = test[1]
#print(upgma(mat,lab))
#temp = upgma(*matrix_from_pairs(val))
#print temp
#temp = upgma(*matrix_from_pairs(pairs))
#print temp
#graph = graph_from_upgma(upgma(*matrix_from_pairs(val)))
graph = graph_from_upgma(upgma(*matrix_from_pairs(pairs)))

#print graph;
size = os.path.getsize(fname)
print('size = ' + str(size))
print "Creating SVG file..."
t = int(time.time())
filename = "output/%s-upgma_graph.svg"%(t)
graph.write_raw("output/upgma_raw.dot")
graph.write_svg(filename)


