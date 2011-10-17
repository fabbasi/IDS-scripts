#!/bin/bash
## Trigger to calculate edit distances across all 10 datasets 
## Invokes alldist-with-graph python script
rm list500.txt
for i in `seq 1 10`
do
	echo $i
	python alldist-with-graph.py /home/fimz/Dev/disk-2/datasets/500-dataset/$i $i
	mv /home/fimz/Dev/scripts/output/* /home/fimz/Dev/disk-2/datasets/500-results/$i/
done
#sh run500-dynamic.sh
