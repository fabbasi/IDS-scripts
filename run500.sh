#!/bin/bash
while read line
do
echo "$line"
python count-cluster-500.py "$line"
done < list500.txt
exit
