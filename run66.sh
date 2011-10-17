#!/bin/bash
while read line
do
echo "$line"
python count-cluster-66.py "$line"
done < list66.txt
exit
