#!/usr/bin/env bash

#Location of main run directory with set setup-im3shape script in.
IM3SHAPE_DIR=$HOME/im3shape-grid
#IM3SHAPE_DIR=/cvmfs/northgrid.gridpp.ac.uk/lsst/testbed/im3shape_dir

MEDS=$1
CAT=$2
OUT=$3
INI=$4

echo $1 $2 $3 $4
pwd
ls

#Run on all objects on the assumption that we split them
#up earlier into separate cat files
FIRST=0
COUNT=10000000000

#Set up im3shape - environment variables, etc

pushd $IM3SHAPE_DIR
source setup-im3shape
popd

#Run im3shape
echo "Pretending to run im3shape but really just printing some things:"
echo "python -m py3shape.analyze_meds2 $MEDS $INI $CAT $OUT $FIRST $COUNT"

#Real run looks like this:
# python -m py3shape.analyze_meds2 $MEDS $INI $CAT $OUT $FIRST $COUNT

#Fake some output
echo "Normally at this point we would run im3shape" >> $OUT.main.txt
echo "But for now, here is the command:" >> $OUT.main.txt
echo "python -m py3shape.analyze_meds2 $MEDS $INI $CAT $OUT $FIRST $COUNT" >> $OUT.main.txt
echo "and here is the start of the ini file:" >> $OUT.main.txt
head $INI >> $OUT.main.txt
echo "and the cat file:" >> $OUT.main.txt
head $CAT >> $OUT.main.txt

echo "Not forgetting the epoch file " >> $OUT.epoch.txt



