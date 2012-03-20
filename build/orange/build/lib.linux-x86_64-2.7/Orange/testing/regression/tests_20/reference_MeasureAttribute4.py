# Description: Shows why ReliefF needs to check the cached neighbours
# Category:    statistics
# Classes:     MeasureAttribute_relief
# Uses:        iris
# Referenced:  MeasureAttribute.htm

import orange
data = orange.ExampleTable("iris")

r1 = orange.MeasureAttribute_relief()
r2 = orange.MeasureAttribute_relief(checkCachedData = False)

print "%.3f\t%.3f" % (r1(0, data), r2(0, data))
for ex in data:
    ex[0] = 0
print "%.3f\t%.3f" % (r1(0, data), r2(0, data))
