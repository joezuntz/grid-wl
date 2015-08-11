#!/usr/bin/env bash

#Parameters of this run
STORAGE_ELEMENT=srm://bohr3226.tier2.hep.manchester.ac.uk/dpm/tier2.hep.manchester.ac.uk/home/vo.northgrid.ac.uk
CODE_DIR=/cvmfs/lsst.opensciencegrid.org/uk/shape-measurement/im3shape/im3shape-2015-08-03
USERNAME=zuntz
DATASET=tb-y1a1-v01
RUN_NUMBER=1
INDIR=$STORAGE_ELEMENT/$USERNAME/$DATASET/
OUTDIR=$STORAGE_ELEMENT/$USERNAME/results/$DATASET/$RUN_NUMBER/

#should be distributed with the code

#Input files, need to be brought from somewhere
MEDS=$1
CAT=$2

#Output file base, $OUT.main.txt and $OUT.epoch.txt need
#to be brought back after run
OUT=$3

#Which part of this file to run.  FIRST is now interpreted as a job index
#our of JOB_COUNT
FIRST=$4
JOB_COUNT=$5

INI=$6

#Dummy value since we are using --split below
COUNT=1


echo Downloading data `date`
#Download/obtain data $MEDS and $CAT somehow
gfal-copy $INDIR/$MEDS file://$PWD/$MEDS

#Run the main code - also sets up environment
echo Running code `date`

#Some of the im3shape variables interfere with the gfal commands, so we will save and restore.
#We should put this in a packaged run_im3shape  script but I want to test it now and there is a three hour
#delay when you update CVFMFS

OLD_PATH=$PATH
OLD_LD=$LD


pwd
#Set up im3shape - paths etc
pushd $CODE_DIR
. setup-im3shape
popd

pwd
ls $CODE_DIR
ls $INI
cat $INI

#Actually tun the code
python -m py3shape.analyze_meds2 $MEDS $INI $CAT $OUT $FIRST $COUNT --split $JOB_COUNT

#Restore old paths so we can run gfal-copy
export PATH=$OLD_PATH
export LD_LIBRARY_PATH=$OLD_LD
unset PYTHON_LIB
unset PYTHON_VERSION
unset PYTHONPATH
unset PYTHONHOME
unset PYTHON_INCLUDE
unset PYTHON_DIR
unset PYTHON_ROOT


echo Copying back results  `date`
# Copy results home somehow
gfal-mkdir -p $OUTDIR
gfal-copy file://$PWD/output.main.txt $OUTDIR/$MEDS.main.$FIRST.txt
gfal-copy file://$PWD/output.epoch.txt $OUTDIR/$MEDS.epoch.$FIRST.txt

echo Complete  `date`
