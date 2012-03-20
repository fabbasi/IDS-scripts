# Description: Self Organizing Maps on iris data set
# Category:    projection
# Uses:        iris
# Referenced:  Orange.projection.som
# Classes:     Orange.projection.som.SOMLearner

import Orange

import random
random.seed(0)

som = Orange.projection.som.SOMLearner(map_shape=(3, 3),
                initialize=Orange.projection.som.InitializeRandom)
map = som(Orange.data.Table("iris.tab"))

print "Node    Instances"
print "\n".join(["%s  %d" % (str(n.pos), len(n.examples)) for n in map])

i, j = 1, 2
print
print "Data instances in cell (%d, %d):" % (i, j)
for e in map[i, j].examples:
    print e