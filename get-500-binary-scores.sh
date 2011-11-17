#!/bin/bash
## Trigger to calculate edit distances across all 10 datasets 
## Invokes alldist-with-graph python script
rm list500.txt
for i in `seq 1 10`
do
	echo $i
	python ncddist-with-graph-for-binary.py /home/fimz/Dev/datasets/500-dataset/binary/$i $i
	mv /home/fimz/Dev/scripts/output/* /home/fimz/Dev/datasets/500-results/binary/$i/
done
#sh run500-dynamic.sh
