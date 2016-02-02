#!/usr/bin/env bash

#Location of main run directory with set setup-im3shape script in.
#IM3SHAPE_DIR=$HOME/im3shape-grid
IM3SHAPE_DIR=/cvmfs/northgrid.gridpp.ac.uk/lsst/im3shape-grid

MEDS=$1
CAT=$2
OUT=$3
INI=$4


#Some debug output to show all the files available
echo $1 $2 $3 $4
echo 
echo Top
ls /cvmfs/northgrid.gridpp.ac.uk/
echo
echo Second
ls /cvmfs/northgrid.gridpp.ac.uk/lsst
echo
echo Third
ls /cvmfs/northgrid.gridpp.ac.uk/lsst/testbed/
echo
echo Fourth
ls $IM3SHAPE_DIR

#Run on all objects on the assumption that we split them
#up earlier into separate cat files
FIRST=0
COUNT=10000000000

#Set up im3shape - environment variables, etc
cd $IM3SHAPE_DIR
source setup-im3shape
cd -

#Real run looks like this:
python -m py3shape.analyze_meds2 $MEDS $INI $CAT $OUT $FIRST $COUNT
