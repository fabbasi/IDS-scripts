#!/bin/bash

## Trigger the Dynamic category parser script for Confusion matrix and ROC creation
## Gets result files from list500.txt created by all-dist script
x=1;
y=1;
rm -f *-500-dyn-result*
while read line
do
echo "$line"
echo $x;
python Dynamic-category-parser.py "$line" "$x"
x=`expr $x + 1`;
if [ $x -eq 7 ]
then
mv *-500-dyn-result* /home/fimz/Dev/datasets/500-results/$y/
echo "Y:"
echo $y
y=`expr $y + 1`;
x=1
fi
done < list500.txt
exit
