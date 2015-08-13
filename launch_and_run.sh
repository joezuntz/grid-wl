#!/usr/bin/env bash

#Echo all commands
set -o xtrace

#Parameters of this run
STORAGE_ELEMENT=srm://bohr3226.tier2.hep.manchester.ac.uk/dpm/tier2.hep.manchester.ac.uk/home/lsst/zuntz
CODE_DIR=/cvmfs/lsst.opensciencegrid.org/uk/shape-measurement/im3shape/im3shape-2015-08-03
INPUT_BASE=meds
OUTPUT_BASE=results
RUN_NUMBER=1

#should be distributed with the code
DATASET=$1

#Input files, need to be brought from somewhere
MEDS=$2
CAT=$3

#Output file base, $OUT.main.txt and $OUT.epoch.txt need
#to be brought back after run
OUT=$4

#Which part of this file to run.  FIRST is now interpreted as a job index
#our of JOB_COUNT
FIRST=$5
JOB_COUNT=$6

INI=$7

#Dummy value since we are using --split below
COUNT=1


INDIR=$STORAGE_ELEMENT/$INPUT_BASE/$DATASET/
OUTDIR=$STORAGE_ELEMENT/$OUTPUT_BASE/v$RUN_NUMBER/$DATASET/

echo Downloading data `date`
#Download/obtain data $MEDS and $CAT somehow
gfal-copy $INDIR/$MEDS file://$PWD/$MEDS 2>&1

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
python -m py3shape.analyze_meds2 $MEDS $INI $CAT $OUT $FIRST $COUNT --split $JOB_COUNT 2>&1

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
gfal-mkdir -p $OUTDIR 2>&1
gfal-copy file://$PWD/output.main.txt $OUTDIR/$MEDS.main.$FIRST.txt 2>&1
gfal-copy file://$PWD/output.epoch.txt $OUTDIR/$MEDS.epoch.$FIRST.txt 2>&1

echo Complete  `date`
