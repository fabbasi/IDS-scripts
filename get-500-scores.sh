#!/bin/bash
## Trigger to calculate edit distances across all 10 datasets 
## Invokes alldist-with-graph python script
## Usage:
## python alldist-with-graph.py /path/to/dataset iteration /path/to/result
## python alldist-with-graph.py /home/fimz/Dev/datasets/500-dataset/$i $i /home/fimz/Dev/datasets/500-results
##
rm list500.txt
for i in `seq 1 3`
do
	echo $i
	python alldist-with-graph.py /home/fimz/Dev/datasets/500-dataset/$i $i /home/fimz/Dev/datasets/500-results
	mv /home/fimz/Dev/scripts/output/* /home/fimz/Dev/datasets/500-results/$i/
done
sh run500-dynamic.sh
