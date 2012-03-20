#!/bin/bash

## Trigger the Dynamic category parser script for Confusion matrix and ROC creation
## Gets result files from list500.txt created by all-dist script
## added result output folder support

EXPECTED_ARGS=1
E_BADARGS=65

if [ $# -ne $EXPECTED_ARGS ]
then
	  echo "Usage: `basename $0` {arg}"
	  echo "Usage: `basename $0` /path/to/result/folder"
	   exit $E_BADARGS
fi



out=$1
x=1;
y=1;
rm -f *-500-dyn-result*
while read line
do

echo "$line"
echo $x;

if [ $x -eq 4 ]
then
python Dynamic-category-parser-composite.py "$line" 3
mv *-500-dyn-result* $1
mv output/* $1
echo "Y:"
echo $y
y=`expr $y + 1`;
x=1
echo "Done"
exit 1
fi

python Dynamic-category-parser-raw.py "$line" "$x"
x=`expr $x + 1`;
echo "$line"

done < list500.txt
exit
